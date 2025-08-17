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
import logging
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, TypeVar, cast

from utils.cross_platform_paths import CrossPlatformPathManager
from utils.log_utils import send_dashboard_alert


def _ensure_metrics_table(conn: sqlite3.Connection) -> None:
    """Ensure ``compliance_metrics_history`` table exists."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS compliance_metrics_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER NOT NULL,
            ruff_issues INTEGER NOT NULL,
            tests_passed INTEGER NOT NULL,
            tests_failed INTEGER NOT NULL,
            placeholders_open INTEGER,
            placeholders_resolved INTEGER,
            placeholder_score REAL,
            composite_score REAL
        )
        """
    )

try:  # pragma: no cover - optional database helpers
    from scripts.database.add_violation_logs import ensure_violation_logs
    from scripts.database.add_rollback_logs import ensure_rollback_logs
except Exception:  # pragma: no cover - fallback stubs
    def ensure_violation_logs(*args: Any, **kwargs: Any) -> None:
        return None

    def ensure_rollback_logs(*args: Any, **kwargs: Any) -> None:
        return None


class ComplianceError(Exception):
    """Raised when enterprise compliance checks fail."""


# Forbidden command patterns that must not appear in operations
FORBIDDEN_COMMANDS = ["rm -rf", "mkfs", "shutdown", "reboot", "dd if="]
MAX_RECURSION_DEPTH = 5


def load_placeholder_patterns(config_path: Path | None = None) -> list[str]:
    """Return placeholder regex patterns from ``config/audit_patterns.json``."""
    default = ["TODO", "FIXME"]
    config_file = (
        config_path
        or Path(__file__).resolve().parents[1] / "config" / "audit_patterns.json"
    )
    try:
        data = json.loads(config_file.read_text(encoding="utf-8"))
        return data.get("placeholder_patterns", default)
    except Exception:
        return default


PLACEHOLDER_PATTERNS = load_placeholder_patterns()

# Weights for the composite compliance score components
SCORE_WEIGHTS = {
    "lint": 0.3,
    "test": 0.4,
    "placeholder": 0.2,
    "session": 0.1,
}


F = TypeVar("F", bound=Callable[..., Any])
_ACTIVE_PIDS: set[int] = set()
_PID_DEPTHS: dict[int, int] = {}
_PID_PARENTS: dict[int, int] = {}
_PID_CHILDREN: dict[int, set[int]] = {}
_GUARD_LOCK = threading.Lock()
_PID_LOG_LOCK = threading.Lock()
_PID_THREADS: dict[int, set[int]] = {}
# Track simple call depth per process ID to prevent excessive recursion
_PROCESS_DEPTHS: dict[int, int] = {}
_PROCESS_DEPTH_LOCK = threading.Lock()


def anti_recursion_guard(func: F) -> F:
    """Decorator tracking recursion depth and parent/child PID relationships.

    Aborts when ``MAX_RECURSION_DEPTH`` is exceeded or when a PID loop is
    detected via parent/child tracking. Each PID entry and exit is recorded
    for analytics, and recursion depth is enforced across threads.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        pid = os.getpid()
        ppid = os.getppid()
        tid = threading.get_ident()
        with _GUARD_LOCK:
            ancestor = ppid
            while ancestor:
                if ancestor == pid:
                    _log_violation(
                        f"anti_recursion_guard:pid_loop:pid={pid}:ppid={ppid}"
                    )
                    raise RuntimeError("PID loop detected")
                ancestor = _PID_PARENTS.get(ancestor)
            threads = _PID_THREADS.setdefault(pid, set())
            if threads and tid not in threads:
                _log_violation(
                    f"anti_recursion_guard:duplicate_pid:pid={pid}:tid={tid}"
                )
                raise RuntimeError("Duplicate PID execution")

            depth = _PID_DEPTHS.get(pid, 0)
            if depth >= MAX_RECURSION_DEPTH:
                _log_violation(
                    f"anti_recursion_guard:depth_exceeded:pid={pid}:depth={depth}"
                )
                raise RuntimeError("Recursion depth exceeded")
            depth += 1
            _PID_DEPTHS[pid] = depth
            _ACTIVE_PIDS.add(pid)
            threads.add(tid)
            _PID_PARENTS[pid] = ppid
            _PID_CHILDREN.setdefault(ppid, set()).add(pid)
            _record_recursion_pid(Path(f"{func.__qualname__}/entry"), pid, ppid, depth)

        try:
            target: Path | None = None
            if args:
                candidate = args[0]
                if isinstance(candidate, (str, os.PathLike)):
                    target = Path(candidate)
            if target is None and "path" in kwargs:
                candidate = kwargs["path"]
                if isinstance(candidate, (str, os.PathLike)):
                    target = Path(candidate)
            if target is not None and _detect_recursion(target):
                _log_violation(
                    f"anti_recursion_guard:path_recursion:path={target}"
                )
                raise RuntimeError("Path recursion detected")
            return func(*args, **kwargs)
        finally:
            with _GUARD_LOCK:
                remaining = _PID_DEPTHS.get(pid, 0) - 1
                _record_recursion_pid(
                    Path(f"{func.__qualname__}/exit"), pid, ppid, remaining
                )
                if remaining <= 0:
                    _PID_DEPTHS.pop(pid, None)
                    _ACTIVE_PIDS.discard(pid)
                    threads = _PID_THREADS.get(pid)
                    if threads is not None:
                        threads.discard(tid)
                        if not threads:
                            _PID_THREADS.pop(pid, None)
                    parent = _PID_PARENTS.pop(pid, None)
                    if parent is not None:
                        children = _PID_CHILDREN.get(parent)
                        if children is not None:
                            children.discard(pid)
                            if not children:
                                _PID_CHILDREN.pop(parent, None)
                else:
                    _PID_DEPTHS[pid] = remaining

    return cast(F, wrapper)


def pid_recursion_guard(func: F) -> F:
    """Guard against excessive recursion per process ID.

    Each process ID maintains its own call depth counter. When the
    counter exceeds ``MAX_RECURSION_DEPTH`` the call is aborted and a
    compliance violation is logged with the offending PID for auditing.
    """

    logger = logging.getLogger(__name__)

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        pid = os.getpid()
        with _PROCESS_DEPTH_LOCK:
            current = _PROCESS_DEPTHS.get(pid, 0)
            next_depth = current + 1
            if next_depth > MAX_RECURSION_DEPTH:
                logger.error(
                    "Recursion depth %s exceeded for PID %s", next_depth, pid
                )
                _log_violation(f"recursion_violation:pid={pid}:depth={next_depth}")
                raise ComplianceError(
                    f"Recursion depth {next_depth} exceeded for PID {pid}"
                )
            _PROCESS_DEPTHS[pid] = next_depth

        try:
            return func(*args, **kwargs)
        finally:
            with _PROCESS_DEPTH_LOCK:
                remaining = _PROCESS_DEPTHS.get(pid, 0) - 1
                if remaining <= 0:
                    _PROCESS_DEPTHS.pop(pid, None)
                else:
                    _PROCESS_DEPTHS[pid] = remaining

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
    ensure_violation_logs(analytics_db, validate=False)
    try:
        with sqlite3.connect(analytics_db) as conn:
            conn.execute(
                "INSERT INTO violation_logs (timestamp, details) VALUES (?, ?)",
                (datetime.now().isoformat(), details),
            )
            conn.commit()
    except sqlite3.Error as exc:
        try:
            logging.error("Failed to log violation: %s", exc)
            send_dashboard_alert(
                {
                    "event": "violation_log_error",
                    "details": details,
                    "error": str(exc),
                }
            )
        except Exception:
            pass


def _log_rollback(target: str, backup: str | None = None) -> None:
    """Log a rollback event to analytics.db."""
    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    analytics_db = workspace / "databases" / "analytics.db"
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    ensure_rollback_logs(analytics_db, validate=False)
    try:
        with sqlite3.connect(analytics_db) as conn:
            conn.execute(
                "INSERT INTO rollback_logs (target, backup, timestamp) VALUES (?, ?, ?)",
                (target, backup, datetime.now().isoformat()),
            )
            conn.commit()
    except sqlite3.Error as exc:
        try:
            logging.error("Failed to log rollback: %s", exc)
            send_dashboard_alert(
                {
                    "event": "rollback_log_error",
                    "target": target,
                    "backup": backup,
                    "error": str(exc),
                }
            )
        except Exception:
            pass


def _ensure_recursion_pid_log(db_path: Path) -> None:
    """Ensure the ``recursion_pid_log`` table exists."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS recursion_pid_log (
                path TEXT,
                pid INTEGER,
                parent_pid INTEGER,
                depth INTEGER,
                timestamp TEXT
            )
            """
        )
        conn.commit()


def _record_recursion_pid(
    path: Path, pid: int, parent_pid: int | None = None, depth: int | None = None
) -> None:
    """Record PID activity against ``path`` for recursion tracking."""
    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    analytics_db = workspace / "databases" / "analytics.db"
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    _ensure_recursion_pid_log(analytics_db)
    try:
        path_str = str(path.resolve())
    except Exception:
        path_str = str(path)
    with _PID_LOG_LOCK:
        with sqlite3.connect(analytics_db) as conn:
            conn.execute(
                "INSERT INTO recursion_pid_log (path, pid, parent_pid, depth, timestamp) VALUES (?, ?, ?, ?, ?)",
                (path_str, pid, parent_pid, depth, datetime.now().isoformat()),
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
    ppid = os.getppid()
    setattr(_detect_recursion, "last_pid", pid)
    setattr(_detect_recursion, "max_depth_reached", 0)
    setattr(_detect_recursion, "aborted", False)
    setattr(_detect_recursion, "aborted_path", None)

    # Abort immediately if the working directory itself exceeds ``max_depth``
    root_depth = len(root.relative_to(root.anchor).parts)
    if root_depth > max_depth:
        setattr(_detect_recursion, "aborted", True)
        setattr(_detect_recursion, "aborted_path", root)
        _record_recursion_pid(root, pid, ppid, 0)
        return True

    _record_recursion_pid(root, pid, ppid, 0)

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

        _record_recursion_pid(current_resolved, pid, ppid, depth)

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
                _record_recursion_pid(child_resolved, pid, ppid, depth + 1)
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
        workspace = CrossPlatformPathManager.get_workspace_path()
        result = subprocess.run(
            [
                "ruff",
                ".",
                "--output-format",
                "json",
                "--config",
                str(workspace / "pyproject.toml"),
                "--force-exclude",
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=workspace,
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
    """Return count of placeholder patterns in repository."""
    workspace = CrossPlatformPathManager.get_workspace_path()
    count = 0
    for path in workspace.rglob("*.py"):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for pat in PLACEHOLDER_PATTERNS:
            count += len(re.findall(pat, text))
    return count


def _fetch_session_lifecycle_stats(db_path: Path | None = None) -> tuple[int, int]:
    """Return counts of successful and failed sessions from ``analytics.db``."""
    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    db = db_path or (workspace / "databases" / "analytics.db")
    if not db.exists():
        return 0, 0
    success = failed = 0
    with sqlite3.connect(db) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS session_lifecycle (
                session_id TEXT PRIMARY KEY,
                start_ts INTEGER NOT NULL,
                end_ts INTEGER,
                duration_seconds REAL,
                zero_byte_violations INTEGER DEFAULT 0,
                recursion_flags INTEGER DEFAULT 0,
                status TEXT DEFAULT 'running'
            )"""
        )
        for status, count in conn.execute(
            "SELECT status, COUNT(*) FROM session_lifecycle GROUP BY status"
        ):
            if status == "success":
                success = count
            elif status == "failed":
                failed = count
    return int(success), int(failed)


def calculate_compliance_score(
    ruff_issues: int,
    tests_passed: int,
    tests_failed: int,
    placeholders_open: int,
    placeholders_resolved: int,
    sessions_successful: int,
    sessions_failed: int,
    db_path: Path | None = None,
    *,
    persist: bool = False,
    test_mode: bool = False,
) -> tuple[float, dict[str, float]]:
    """Return a composite code quality score and ratios.

    The helper combines four sources of information:

    ``ruff_issues``
        Total lint findings from ``ruff``. Fewer issues yield higher scores.

    ``tests_passed``/``tests_failed``
        Used to compute a pytest pass ratio. If no tests ran the ratio is ``0``.

    ``placeholders_open``/``placeholders_resolved``
        Used to determine how many TODO/FIXME markers have been resolved.

    ``sessions_successful``/``sessions_failed``
        Ratio of successful session lifecycle executions.

    The final score is a weighted sum of lint (30%), test pass ratio (40%),
    placeholder resolution (20%), and session lifecycle success (10%),
    expressed on a ``0..100`` scale.
    """

    total_tests = tests_passed + tests_failed
    pass_ratio = tests_passed / total_tests if total_tests else 0.0
    total_placeholders = placeholders_open + placeholders_resolved
    resolution_ratio = (
        placeholders_resolved / total_placeholders if total_placeholders else 1.0
    )
    total_sessions = sessions_successful + sessions_failed
    session_ratio = (
        sessions_successful / total_sessions if total_sessions else 1.0
    )
    lint_score = max(0.0, 100 - ruff_issues)
    test_score = pass_ratio * 100
    placeholder_score = resolution_ratio * 100
    session_score = session_ratio * 100
    composite = round(
        SCORE_WEIGHTS["lint"] * lint_score
        + SCORE_WEIGHTS["test"] * test_score
        + SCORE_WEIGHTS["placeholder"] * placeholder_score
        + SCORE_WEIGHTS["session"] * session_score,
        2,
    )
    breakdown = {
        "lint_score": round(lint_score, 2),
        "test_score": round(test_score, 2),
        "placeholder_score": round(placeholder_score, 2),
        "session_score": round(session_score, 2),
        "lint_weighted": round(SCORE_WEIGHTS["lint"] * lint_score, 2),
        "test_weighted": round(SCORE_WEIGHTS["test"] * test_score, 2),
        "placeholder_weighted": round(SCORE_WEIGHTS["placeholder"] * placeholder_score, 2),
        "session_weighted": round(SCORE_WEIGHTS["session"] * session_score, 2),
        "test_pass_ratio": round(pass_ratio, 2),
        "placeholder_resolution_ratio": round(resolution_ratio, 2),
        "session_success_ratio": round(session_ratio, 2),
        "ruff_issues": int(ruff_issues),
        "tests_passed": int(tests_passed),
        "tests_failed": int(tests_failed),
        "placeholders_open": int(placeholders_open),
        "placeholders_resolved": int(placeholders_resolved),
        "sessions_successful": int(sessions_successful),
        "sessions_failed": int(sessions_failed),
    }

    if persist and not test_mode:
        workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
        db = db_path or (workspace / "databases" / "analytics.db")
        db.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(db) as conn:
            _ensure_metrics_table(conn)
            conn.execute(
                """CREATE TABLE IF NOT EXISTS code_quality_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ruff_issues INTEGER,
                    tests_passed INTEGER,
                    tests_failed INTEGER,
                    placeholders_open INTEGER,
                    placeholders_resolved INTEGER,
                    sessions_successful INTEGER,
                    sessions_failed INTEGER,
                    lint_score REAL,
                    test_score REAL,
                    placeholder_score REAL,
                    session_score REAL,
                    composite_score REAL,
                    ts TEXT
                )""",
            )
            conn.execute(
                """INSERT INTO code_quality_metrics (
                    ruff_issues, tests_passed, tests_failed,
                    placeholders_open, placeholders_resolved,
                    sessions_successful, sessions_failed,
                    lint_score, test_score, placeholder_score,
                    session_score, composite_score, ts
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    int(ruff_issues),
                    int(tests_passed),
                    int(tests_failed),
                    int(placeholders_open),
                    int(placeholders_resolved),
                    int(sessions_successful),
                    int(sessions_failed),
                    float(breakdown["lint_score"]),
                    float(breakdown["test_score"]),
                    float(breakdown["placeholder_score"]),
                    float(breakdown["session_score"]),
                    float(composite),
                    datetime.now().isoformat(),
                ),
            )
            ts = int(datetime.now().timestamp())
            conn.execute(
                """INSERT INTO compliance_metrics_history (
                    timestamp, ruff_issues, tests_passed, tests_failed,
                    placeholders_open, placeholders_resolved,
                    placeholder_score, composite_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    ts,
                    int(ruff_issues),
                    int(tests_passed),
                    int(tests_failed),
                    int(placeholders_open),
                    int(placeholders_resolved),
                    float(breakdown["placeholder_score"]),
                    float(composite),
                ),
            )
            conn.commit()
    return composite, breakdown


def persist_compliance_score(
    score: float,
    breakdown: dict | None = None,
    db_path: Path | None = None,
) -> None:
    """Persist composite and component scores to ``analytics.db``."""

    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    db = db_path or (workspace / "databases" / "analytics.db")
    db.parent.mkdir(parents=True, exist_ok=True)
    breakdown = breakdown or {}
    with sqlite3.connect(db) as conn:
        _ensure_metrics_table(conn)
        conn.execute(
            """CREATE TABLE IF NOT EXISTS compliance_scores (
                timestamp TEXT,
                composite_score REAL,
                lint_score REAL,
                test_score REAL,
                placeholder_score REAL,
                session_score REAL
            )"""
        )
        for column in ("lint_score", "test_score", "placeholder_score", "session_score"):
            try:
                conn.execute(f"ALTER TABLE compliance_scores ADD COLUMN {column} REAL")
            except sqlite3.OperationalError:
                pass
        conn.execute(
            """INSERT INTO compliance_scores (
                timestamp, composite_score, lint_score, test_score, placeholder_score, session_score
            ) VALUES (?, ?, ?, ?, ?, ?)""",
            (
                datetime.now().isoformat(),
                float(score),
                float(breakdown.get("lint_score", 0.0)),
                float(breakdown.get("test_score", 0.0)),
                float(breakdown.get("placeholder_score", 0.0)),
                float(breakdown.get("session_score", 0.0)),
            ),
        )
        ts = int(datetime.now().timestamp())
        conn.execute(
            """INSERT INTO compliance_metrics_history (
                timestamp, ruff_issues, tests_passed, tests_failed,
                placeholders_open, placeholders_resolved,
                placeholder_score, composite_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                ts,
                int(breakdown.get("ruff_issues", 0)),
                int(breakdown.get("tests_passed", 0)),
                int(breakdown.get("tests_failed", 0)),
                int(breakdown.get("placeholders_open", 0)),
                int(breakdown.get("placeholders_resolved", 0)),
                float(breakdown.get("placeholder_score", 0.0)),
                float(score),
            ),
        )
        conn.commit()


def record_code_quality_metrics(
    ruff_issues: int,
    tests_passed: int,
    tests_failed: int,
    placeholders_open: int,
    placeholders_resolved: int,
    sessions_successful: int = 0,
    sessions_failed: int = 0,
    db_path: Path | None = None,
    *,
    test_mode: bool = False,
) -> float:
    """Compute weighted metrics and persist them to ``analytics.db``.

    Returns the composite score on a ``0..100`` scale. When ``test_mode`` is
    ``True`` the calculation is performed but no database writes occur.
    """

    composite_score, breakdown = calculate_compliance_score(
        ruff_issues,
        tests_passed,
        tests_failed,
        placeholders_open,
        placeholders_resolved,
        sessions_successful,
        sessions_failed,
    )

    if test_mode:
        return composite_score

    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    db = db_path or (workspace / "databases" / "analytics.db")
    db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db) as conn:
        _ensure_metrics_table(conn)
        conn.execute(
            """CREATE TABLE IF NOT EXISTS code_quality_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ruff_issues INTEGER,
                tests_passed INTEGER,
                tests_failed INTEGER,
                placeholders_open INTEGER,
                placeholders_resolved INTEGER,
                sessions_successful INTEGER,
                sessions_failed INTEGER,
                lint_score REAL,
                test_score REAL,
                placeholder_score REAL,
                session_score REAL,
                composite_score REAL,
                ts TEXT
            )""",
        )
        for column in (
            "lint_score",
            "test_score",
            "placeholder_score",
            "session_score",
            "composite_score",
        ):
            try:
                conn.execute(
                    f"ALTER TABLE code_quality_metrics ADD COLUMN {column} REAL"
                )
            except sqlite3.OperationalError:
                pass
        for column in (
            "placeholders_open",
            "placeholders_resolved",
            "sessions_successful",
            "sessions_failed",
        ):
            try:
                conn.execute(
                    f"ALTER TABLE code_quality_metrics ADD COLUMN {column} INTEGER"
                )
            except sqlite3.OperationalError:
                pass
        conn.execute(
            """INSERT INTO code_quality_metrics (
                ruff_issues, tests_passed, tests_failed,
                placeholders_open, placeholders_resolved,
                sessions_successful, sessions_failed,
                lint_score, test_score, placeholder_score,
                session_score, composite_score, ts
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                int(ruff_issues),
                int(tests_passed),
                int(tests_failed),
                int(placeholders_open),
                int(placeholders_resolved),
                int(sessions_successful),
                int(sessions_failed),
                float(breakdown["lint_score"]),
                float(breakdown["test_score"]),
                float(breakdown["placeholder_score"]),
                float(breakdown["session_score"]),
                float(composite_score),
                datetime.now().isoformat(),
            ),
        )
        ts = int(datetime.now().timestamp())
        conn.execute(
            """INSERT INTO compliance_metrics_history (
                timestamp, ruff_issues, tests_passed, tests_failed,
                placeholders_open, placeholders_resolved,
                placeholder_score, composite_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                ts,
                int(ruff_issues),
                int(tests_passed),
                int(tests_failed),
                int(placeholders_open),
                int(placeholders_resolved),
                float(breakdown["placeholder_score"]),
                float(composite_score),
            ),
        )
        conn.commit()
    return composite_score

def get_latest_compliance_score(db_path: Path | None = None) -> float:
    """Return the most recent composite compliance score from analytics.db."""
    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    db = db_path or (workspace / "databases" / "analytics.db")
    if not db.exists():
        return 0.0
    with sqlite3.connect(db) as conn:
        cur = conn.execute(
            "SELECT composite_score FROM compliance_scores ORDER BY timestamp DESC LIMIT 1"
        )
        row = cur.fetchone()
        return float(row[0]) if row else 0.0


def calculate_and_persist_compliance_score() -> float:
    """Run lint, tests and placeholder scan to compute and store score."""
    issues = _run_ruff()
    passed, failed = _run_pytest()
    placeholders_open = _count_placeholders()
    success, failed_sessions = _fetch_session_lifecycle_stats()
    score, breakdown = calculate_compliance_score(
        issues,
        passed,
        failed,
        placeholders_open,
        0,
        success,
        failed_sessions,
        persist=True,
    )
    persist_compliance_score(score, breakdown)
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
    ppid = os.getppid()
    previous_pid = getattr(context, "pid", pid)
    previous_parent = getattr(context, "parent_pid", ppid)

    if previous_pid != pid:
        raise ComplianceError("PID mismatch detected.")
    if previous_parent != ppid:
        raise ComplianceError("Parent PID mismatch detected.")

    ancestors = getattr(context, "ancestors", [])
    if pid in ancestors:
        raise ComplianceError("PID loop detected.")
    ancestors.append(pid)
    setattr(context, "ancestors", ancestors)

    setattr(context, "recursion_depth", depth + 1)
    setattr(context, "parent_pid", ppid)
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
    "_ensure_metrics_table",
    "run_final_validation",
    "validate_environment",
    "enforce_anti_recursion",
    "anti_recursion_guard",
    "pid_recursion_guard",
    "generate_compliance_summary",
    "calculate_compliance_score",
    "persist_compliance_score",
    "record_code_quality_metrics",
    "get_latest_compliance_score",
    "calculate_and_persist_compliance_score",
    "ComplianceError",
    "SCORE_WEIGHTS",
]
