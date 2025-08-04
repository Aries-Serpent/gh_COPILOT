from __future__ import annotations

"""Enterprise compliance helpers and enforcement routines."""

import os
import shutil
import sqlite3
import sys
import json
from datetime import datetime
from pathlib import Path

from utils.cross_platform_paths import CrossPlatformPathManager
from utils.log_utils import send_dashboard_alert

from scripts.database.add_violation_logs import ensure_violation_logs
from scripts.database.add_rollback_logs import ensure_rollback_logs
from scripts.validation.dual_copilot_orchestrator import DualCopilotOrchestrator


class ComplianceError(Exception):
    """Raised when enterprise compliance checks fail."""


# Forbidden command patterns that must not appear in operations
FORBIDDEN_COMMANDS = ["rm -rf", "mkfs", "shutdown", "reboot", "dd if="]
MAX_RECURSION_DEPTH = 5


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


def _detect_recursion(path: Path) -> bool:
    """Return True if ``path`` contains a nested folder matching itself."""
    root = path.resolve()
    for folder in path.rglob(path.name):
        if folder.is_dir() and folder != path:
            try:
                folder.resolve().relative_to(root)
            except ValueError:
                continue
            return True
    return False


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

    setattr(context, "recursion_depth", depth + 1)
    setattr(context, "parent_pid", os.getppid())
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

    if _detect_recursion(workspace):
        _log_violation("recursive_workspace")
        send_dashboard_alert({"event": "recursive_workspace", "path": str(workspace)})
        violations.append("recursive_workspace")

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

    if _detect_recursion(path):
        _log_violation("recursive_target")
        send_dashboard_alert({"event": "recursive_target", "path": str(path)})
        violations.append("recursive_target")

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
    "generate_compliance_summary",
    "ComplianceError",
]
