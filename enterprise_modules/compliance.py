from __future__ import annotations

"""Enterprise compliance helpers and enforcement routines."""

import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

from scripts.database.add_violation_logs import ensure_violation_logs


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


def validate_enterprise_operation(target_path: str | None = None) -> bool:
    """Ensure operations comply with backup and path policies."""
    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    backup_root = Path(os.getenv("GH_COPILOT_BACKUP_ROOT", "/tmp/gh_COPILOT_Backups"))
    path = Path(target_path or workspace)

    violations = []

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

    # Cleanup forbidden backup folders within workspace
    for item in workspace.rglob("*backup*"):
        if item.is_dir() and item != backup_root and workspace in item.parents:
            shutil.rmtree(item, ignore_errors=True)
            violations.append(f"removed_forbidden:{item}")

    for violation in violations:
        _log_violation(violation)

    return not violations


__all__ = ["validate_enterprise_operation"]
