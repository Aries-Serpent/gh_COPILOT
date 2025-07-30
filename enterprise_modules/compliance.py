from __future__ import annotations

"""Enterprise compliance helpers and enforcement routines."""

import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

from utils.cross_platform_paths import CrossPlatformPathManager

from scripts.database.add_violation_logs import ensure_violation_logs
from scripts.database.add_rollback_logs import ensure_rollback_logs

# Forbidden command patterns that must not appear in operations
FORBIDDEN_COMMANDS = [
    "rm -rf",
    "mkfs",
    "shutdown",
    "reboot",
    "dd if="
]


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
    """Return True if ``path`` contains recursive subfolders."""
    root_name = path.name.lower()
    for folder in path.rglob(root_name):
        if folder.is_dir() and folder != path:
            return True
    return False


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
        violations.append("recursive_workspace")

    # Disallow backup directories inside the workspace
    if backup_root.resolve().as_posix().startswith(workspace.resolve().as_posix()):
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
        violations.append("recursive_target")

    # Cleanup forbidden backup folders within workspace
    for item in workspace.rglob("*backup*"):
        if item.is_dir() and item != backup_root and workspace in item.parents:
            shutil.rmtree(item, ignore_errors=True)
            violations.append(f"removed_forbidden:{item}")

    for violation in violations:
        if violation in {"recursive_workspace", "recursive_target"}:
            continue
        _log_violation(violation)

    return not violations


__all__ = ["validate_enterprise_operation", "_log_rollback"]
