from __future__ import annotations

"""Enterprise compliance helpers and enforcement routines."""

import os
import re
import shutil
import sqlite3
import subprocess
import sys
import json
import threading
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, TypeVar, cast

from utils.cross_platform_paths import CrossPlatformPathManager
from utils.log_utils import send_dashboard_alert

from scripts.database.add_violation_logs import ensure_violation_logs
from scripts.database.add_rollback_logs import ensure_rollback_logs


class ComplianceError(Exception):
    """Raised when enterprise compliance checks fail."""


# Forbidden command patterns that must not appear in operations
FORBIDDEN_COMMANDS = ["rm -rf", "mkfs", "shutdown", "reboot", "dd if="]
MAX_RECURSION_DEPTH = 5
PLACEHOLDER_PATTERNS = ["TODO", "FIXME"]


F = TypeVar("F", bound=Callable[..., Any])
_ACTIVE_PIDS: set[int] = set()
_PID_DEPTHS: dict[int, int] = {}
_GUARD_LOCK = threading.Lock()


def anti_recursion_guard(func: F) -> F:
    """Decorator tracking recursion depth and active PIDs.

    Aborts when ``MAX_RECURSION_DEPTH`` is exceeded or when the current PID
    attempts to re-enter while still active.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        pid = os.getpid()
        with _GUARD_LOCK:
            depth = _PID_DEPTHS.get(pid, 0)
            if depth >= MAX_RECURSION_DEPTH:
                raise RuntimeError("Recursion depth exceeded")
            if pid in _ACTIVE_PIDS:
                raise RuntimeError("PID already active")
            _PID_DEPTHS[pid] = depth + 1
            _ACTIVE_PIDS.add(pid)

        try:
            return func(*args, **kwargs)
        finally:
            with _GUARD_LOCK:
                remaining = _PID_DEPTHS.get(pid, 0) - 1
                if remaining <= 0:
                    _PID_DEPTHS.pop(pid, None)
                    _ACTIVE_PIDS.discard(pid)
                else:
                    _PID_DEPTHS[pid] = remaining

    return cast(F, wrapper)


def _load_forbidden_paths() -> list[str]:
    """Return policy-defined forbidden path patterns."""
    workspace = CrossPlatformPathManager.get_workspace_path()
    config_file = os.getenv("CONFIG_PATH")
    if config_file is None:
        config_file = workspace / "config" / "enterprise.json"
    else:
        config_file = Path(config_file)

    try:
        with open(config_file, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        patterns = data.get("forbidden_paths", [])
        if isinstance(patterns, list):
            return [str(p) for p in patterns]
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return []


def _log_violation(details: str) -> None:
    """Log a compliance violation to analytics.db."""
    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    analytics_db = workspace / "databases" / "analytics.db"
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    ensure_violation_logs(analytics_db)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            "INSERT INTO violation_logs (timestamp, details) VALUES (?, ?)",
            (datetime.now().isoformat(), details),
        )
        conn.commit()


def _log_rollback(target: str, backup: str | None = None) -> None:
    """Log a rollback event to analytics.db."""
    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    analytics_db = workspace / "databases" / "analytics.db"
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    ensure_rollback_logs(analytics_db)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            "INSERT INTO rollback_logs (target, backup, timestamp) VALUES (?, ?, ?)",
            (target, backup, datetime.now().isoformat()),
        )
        conn.commit()


def _ensure_recursion_pid_log(db_path: Path) -> None:
    """Ensure the ``recursion_pid_log`` table exists."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS recursion_pid_log (path TEXT, pid INTEGER, timestamp TEXT)"
        )
        conn.commit()


def _record_recursion_pid(path: Path, pid: int) -> None:
    """Record ``pid`` executions against ``path`` for recursion tracking."""
    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    analytics_db = workspace / "databases" / "analytics.db"
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    _ensure_recursion_pid_log(analytics_db)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            "INSERT INTO recursion_pid_log (path, pid, timestamp) VALUES (?, ?, ?)",
            (str(path.resolve()), pid, datetime.now().isoformat()),
        )
        conn.commit()


def _detect_recursion(path: Path, *, max_depth: int = MAX_RECURSION_DEPTH) -> bool:
    """Return True if ``path`` contains a nested folder matching itself or
    exceeds ``max_depth`` during traversal.

    The search records the process ID of the caller to ``last_pid`` for
    diagnostic purposes. It also tracks the deepest level visited via
    ``max_depth_reached`` and sets an ``aborted`` flag when the traversal
    exceeds ``max_depth``. This prevents runaway recursive scans across nested
    directories and exposes diagnostic information for tests.
    """
    root = path.resolve()
    pid = os.getpid()
    setattr(_detect_recursion, "last_pid", pid)
    setattr(_detect_recursion, "max_depth_reached", 0)
    setattr(_detect_recursion, "aborted", False)
    setattr(_detect_recursion, "aborted_path", None)

    # Abort immediately if the working directory itself exceeds ``max_depth``
    root_depth = len(root.relative_to(root.anchor).parts)
    if root_depth > max_depth:
        setattr(_detect_recursion, "aborted", True)
        setattr(_detect_recursion, "aborted_path", root)
        _record_recursion_pid(root, pid)
        return True

    _record_recursion_pid(root, pid)

    visited: set[Path] = set()

    def _walk(current: Path, depth: int) -> bool:
        setattr(
            _detect_recursion,
            "max_depth_reached",
            max(getattr(_detect_recursion, "max_depth_reached"), depth),
        )
        try:
            current_resolved = current.resolve()
        except OSError:
            return False

        _record_recursion_pid(current_resolved, pid)

        if depth > max_depth:
            setattr(_detect_recursion, "aborted", True)
            setattr(_detect_recursion, "aborted_path", current_resolved)
            return True

        if current_resolved in visited:
            return True
        visited.add(current_resolved)

        for child in current.iterdir():
            if not child.is_dir():
                continue
            try:
                child_resolved = child.resolve()
            except OSError:
                continue
            if child.name == root.name and child != root:
                _record_recursion_pid(child_resolved, pid)
                try:
                    child_resolved.relative_to(root)
                except ValueError:
                    pass
                else:
                    return True
            if _walk(child, depth + 1):
                return True
        return False

    return _walk(root, 0)


def _run_ruff() -> int:
    """Return the number of lint issues reported by Ruff."""
    try:
        result = subprocess.run(
            ["ruff", ".", "--output-format", "json"],
            check=False,
            capture_output=True,
            text=True,
        )
        return len(json.loads(result.stdout or "[]"))
    except Exception:  # pragma: no cover - lint fallback
        return 0


def _run_pytest() -> tuple[int, int]:
    """Return numbers of passed and failed tests from pytest."""
    try:
        result = subprocess.run(
            ["pytest", "-q"],
            check=False,
            capture_output=True,
            text=True,
        )
        m_pass = re.search(r"(\d+) passed", result.stdout)
        m_fail = re.search(r"(\d+) failed", result.stdout)
        passed = int(m_pass.group(1)) if m_pass else 0
        failed = int(m_fail.group(1)) if m_fail else 0
        return passed, failed
    except Exception:  # pragma: no cover - test fallback
        return 0, 0


def _count_placeholders() -> int:
    """Return count of placeholder patterns (TODO/FIXME) in repository."""
    workspace = CrossPlatformPathManager.get_workspace_path()
    count = 0
    for path in workspace.rglob("*.py"):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for pat in PLACEHOLDER_PATTERNS:
            count += text.count(pat)
    return count


def calculate_compliance_score(
    ruff_issues: int,
    tests_passed: int,
    tests_failed: int,
    placeholders_open: int,
    placeholders_resolved: int,
) -> float:
    """Return overall code-quality score on a ``0..100`` scale.

    The score is the mean of three component scores:

    ``lint_score``
        ``max(0, 100 - ruff_issues)``

    ``test_score``
        ``(tests_passed / total_tests) * 100`` where ``total_tests`` is the sum
        of passed and failed tests. If no tests ran, this component is ``0``.

    ``placeholder_score``
        ``(placeholders_resolved / total_placeholders) * 100`` where
        ``total_placeholders`` is the sum of open and resolved placeholders. If
        no placeholders were found the component defaults to ``100``.
    """

    lint_score = max(0.0, 100 - ruff_issues)
    total_tests = tests_passed + tests_failed
    test_score = (tests_passed / total_tests * 100) if total_tests else 0.0
    total_placeholders = placeholders_open + placeholders_resolved
    placeholder_score = (
        placeholders_resolved / total_placeholders * 100
        if total_placeholders
        else 100.0
    )
    return round((lint_score + test_score + placeholder_score) / 3, 2)


def calculate_composite_score(
    ruff_issues: int,
    tests_passed: int,
    tests_failed: int,
    placeholders_open: int,
    placeholders_resolved: int,
) -> tuple[float, dict]:
    """Return composite score and component breakdown on a 0–100 scale."""

    score = calculate_compliance_score(
        ruff_issues,
        tests_passed,
        tests_failed,
        placeholders_open,
        placeholders_resolved,
    )
    breakdown = {
        "ruff_issues": ruff_issues,
        "tests_passed": tests_passed,
        "tests_failed": tests_failed,
        "placeholders_open": placeholders_open,
        "placeholders_resolved": placeholders_resolved,
        "lint_score": max(0.0, 100 - ruff_issues),
        "test_score": (
            tests_passed / (tests_passed + tests_failed) * 100
            if (tests_passed + tests_failed)
            else 0.0
        ),
        "placeholder_score": (
            placeholders_resolved
            / (placeholders_open + placeholders_resolved)
            * 100
            if (placeholders_open + placeholders_resolved)
            else 100.0
        ),
    }
    return score, breakdown


def persist_compliance_score(score: float, db_path: Path | None = None) -> None:
    """Persist ``score`` to the ``compliance_scores`` table in analytics.db."""
    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    db = db_path or (workspace / "databases" / "analytics.db")
    db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS compliance_scores (timestamp TEXT, score REAL)"
        )
        conn.execute(
            "INSERT INTO compliance_scores (timestamp, score) VALUES (?, ?)",
            (datetime.now().isoformat(), float(score)),
        )
        conn.commit()


def record_code_quality_metrics(
    ruff_issues: int,
    tests_passed: int,
    tests_failed: int,
    placeholders_open: int,
    placeholders_resolved: int,
    composite_score: float,
    db_path: Path | None = None,
    *,
    test_mode: bool = False,
) -> None:
    """Store code quality metrics in ``code_quality_metrics`` table."""

    if test_mode:
        return

    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    db = db_path or (workspace / "databases" / "analytics.db")
    db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS code_quality_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ruff_issues INTEGER,
                tests_passed INTEGER,
                tests_failed INTEGER,
                placeholders_open INTEGER,
                placeholders_resolved INTEGER,
                composite_score REAL,
                ts TEXT
            )"""
        )
        try:
            conn.execute(
                "ALTER TABLE code_quality_metrics ADD COLUMN placeholders_open INTEGER"
            )
        except sqlite3.OperationalError:
            pass
        try:
            conn.execute(
                "ALTER TABLE code_quality_metrics ADD COLUMN placeholders_resolved INTEGER"
            )
        except sqlite3.OperationalError:
            pass
        conn.execute(
            """INSERT INTO code_quality_metrics (
                ruff_issues, tests_passed, tests_failed,
                placeholders_open, placeholders_resolved,
                composite_score, ts
            ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                int(ruff_issues),
                int(tests_passed),
                int(tests_failed),
                int(placeholders_open),
                int(placeholders_resolved),
                float(composite_score),
                datetime.now().isoformat(),
            ),
        )
        conn.commit()

def get_latest_compliance_score(db_path: Path | None = None) -> float:
    """Return the most recent compliance score from analytics.db."""
    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    db = db_path or (workspace / "databases" / "analytics.db")
    if not db.exists():
        return 0.0
    with sqlite3.connect(db) as conn:
        cur = conn.execute(
            "SELECT score FROM compliance_scores ORDER BY timestamp DESC LIMIT 1"
        )
        row = cur.fetchone()
        return float(row[0]) if row else 0.0


def calculate_and_persist_compliance_score() -> float:
    """Run lint, tests and placeholder scan to compute and store score."""
    issues = _run_ruff()
    passed, failed = _run_pytest()
    placeholders_open = _count_placeholders()
    score = calculate_compliance_score(
        issues, passed, failed, placeholders_open, 0
    )
    persist_compliance_score(score)
    send_dashboard_alert({"event": "compliance_score", "score": score})
    return score


def generate_compliance_summary() -> dict:
    """Aggregate violation and rollback metrics for dashboards.

    Returns a dictionary with counts of logged compliance violations and
    rollbacks sourced from ``analytics.db``. A dashboard alert is emitted to
    expose the current compliance posture.
    """
    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    analytics_db = workspace / "databases" / "analytics.db"
    if not analytics_db.exists():
        summary = {"violations": 0, "rollbacks": 0}
        send_dashboard_alert({"event": "compliance_summary", **summary})
        return summary

    with sqlite3.connect(analytics_db) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM violation_logs")
        violations = cur.fetchone()[0]
        cur = conn.execute("SELECT COUNT(*) FROM rollback_logs")
        rollbacks = cur.fetchone()[0]

    summary = {"violations": violations, "rollbacks": rollbacks}
    send_dashboard_alert({"event": "compliance_summary", **summary})
    return summary


def validate_environment() -> bool:
    """Run baseline environment checks.

    The workspace must contain ``production.db`` and be readable and writable.
    """

    def check_python_version() -> bool:
        return sys.version_info >= (3, 8)

    def check_required_files() -> bool:
        workspace = CrossPlatformPathManager.get_workspace_path()
        return (workspace / "production.db").exists()

    def check_permissions() -> bool:
        workspace = CrossPlatformPathManager.get_workspace_path()
        return os.access(workspace, os.R_OK | os.W_OK)

    checks = [check_python_version, check_required_files, check_permissions]
    for check in checks:
        if not check():
            raise ComplianceError(
                f"Compliance validation failed: {check.__name__}"
            )
    return True


def enforce_anti_recursion(context: object) -> bool:
    """Ensure recursion depth does not exceed ``MAX_RECURSION_DEPTH``.

    Records the parent process ID on the context and increments the
    ``recursion_depth`` attribute for nested invocations.
    """
    depth = getattr(context, "recursion_depth", 0)
    if depth >= MAX_RECURSION_DEPTH:
        raise ComplianceError("Recursion limit exceeded.")
    pid = os.getpid()
    previous_pid = getattr(context, "pid", pid)
    if previous_pid != pid:
        raise ComplianceError("PID mismatch detected.")

    setattr(context, "recursion_depth", depth + 1)
    setattr(context, "parent_pid", os.getppid())
    setattr(context, "pid", pid)
    return True


def validate_enterprise_operation(
    target_path: str | None = None,
    *,
    command: str | None = None,
) -> bool:
    """Ensure operations comply with backup, path, and command policies."""
    workspace = CrossPlatformPathManager.get_workspace_path()
    backup_root = CrossPlatformPathManager.get_backup_root()
    path = Path(target_path or workspace)

    violations = []

    if command:
        lower = command.lower()
        for pat in FORBIDDEN_COMMANDS:
            if pat in lower:
                violations.append(f"forbidden_command:{pat}")
                break
    recursion_flag = False
    if _detect_recursion(workspace):
        _log_violation("recursive_workspace")
        send_dashboard_alert({"event": "recursive_workspace", "path": str(workspace)})
        violations.append("recursive_workspace")
        recursion_flag = True

    if _detect_recursion(path):
        _log_violation("recursive_target")
        send_dashboard_alert({"event": "recursive_target", "path": str(path)})
        violations.append("recursive_target")
        recursion_flag = True

    if recursion_flag:
        return False

    # Disallow backup directories inside the workspace
    # Ensure the backup root is truly outside the workspace. Using
    # ``Path.is_relative_to`` is available in Python 3.9+. Use a fallback so
    # the check works on Python 3.8 as well.
    try:
        backup_root.resolve().relative_to(workspace.resolve())
    except ValueError:
        pass
    else:
        violations.append("backup_root_inside_workspace")

    if path.resolve().as_posix().startswith(backup_root.resolve().as_posix()):
        violations.append("operation_within_backup_root")

    # Disallow operations in C:/temp
    if str(path).lower().startswith("c:/temp"):
        violations.append("forbidden_system_temp")

    for parent in path.parents:
        if parent == workspace:
            break
        if parent.name.lower().startswith("backup"):
            violations.append(f"forbidden_subpath:{parent}")

    # Cleanup forbidden backup folders within workspace
    venv_path = workspace / ".venv"
    for item in workspace.rglob("*backup*"):
        if item.is_dir() and item != backup_root and workspace in item.parents and venv_path not in item.parents:
            shutil.rmtree(item, ignore_errors=True)
            violations.append(f"removed_forbidden:{item}")

    # Apply configurable forbidden path patterns
    for pat in _load_forbidden_paths():
        for item in workspace.rglob(pat):
            try:
                item.resolve().relative_to(venv_path.resolve())
                continue
            except ValueError:
                pass

            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
            else:
                item.unlink(missing_ok=True)
            violations.append(f"policy_forbidden:{item}")

    for violation in violations:
        if violation in {"recursive_workspace", "recursive_target"}:
            continue
        _log_violation(violation)

    return not violations


def run_final_validation(primary_callable, targets) -> tuple[bool, bool, dict]:
    """Run DualCopilotOrchestrator and expose detailed validator metrics."""
    from scripts.validation.dual_copilot_orchestrator import (
        DualCopilotOrchestrator,
    )

    orchestrator = DualCopilotOrchestrator()
    primary_success, validation_success, metrics = orchestrator.run(
        primary_callable, targets
    )
    return primary_success, validation_success, metrics


__all__ = [
    "validate_enterprise_operation",
    "_log_rollback",
    "run_final_validation",
    "validate_environment",
    "enforce_anti_recursion",
    "anti_recursion_guard",
    "generate_compliance_summary",
    "calculate_compliance_score",
    "persist_compliance_score",
    "calculate_composite_score",
    "record_code_quality_metrics",
    "get_latest_compliance_score",
    "calculate_and_persist_compliance_score",
    "ComplianceError",
]
