"""Unified Disaster Recovery System public interface.

This module exposes the :class:`UnifiedDisasterRecoverySystem` class along with
helper utilities for scheduling backups and logging compliance events. The
actual implementation lives in ``scripts.utilities.unified_disaster_recovery_system``
but we keep this thin wrapper so downstream code can simply import from
``unified_disaster_recovery_system``.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

from utils import log_utils as enterprise_logging


def log_backup_event(event: str, details: Optional[Dict[str, Any]] = None) -> None:
    """Record a compliance event for disaster recovery operations.

    Parameters
    ----------
    event:
        A short event name describing the action.
    details:
        Optional dictionary with extra context to include in the log record.
    """

    payload = {"module": "disaster_recovery", "event": event}
    if details:
        payload.update(details)
    enterprise_logging.log_event(payload)


from scripts.utilities.unified_disaster_recovery_system import (  # noqa: E402
    BackupScheduler,
    ComplianceLogger,
    RestoreExecutor,
    UnifiedDisasterRecoverySystem as _UnifiedDisasterRecoverySystem,
)


def get_compliance_logger() -> ComplianceLogger:
    """Return a :class:`ComplianceLogger` configured for the workspace."""

    return ComplianceLogger()


def get_backup_scheduler(
    workspace_path: str | Path | None = None, logger: ComplianceLogger | None = None
) -> BackupScheduler:
    """Create a :class:`BackupScheduler` for ``workspace_path``.

    Parameters
    ----------
    workspace_path:
        Optional path to the workspace root. Defaults to ``GH_COPILOT_WORKSPACE``
        or ``."`` when not provided.
    logger:
        Pre-configured :class:`ComplianceLogger`. A new logger is created when
        omitted.
    """

    workspace = Path(workspace_path or os.getenv("GH_COPILOT_WORKSPACE", "."))
    return BackupScheduler(workspace, logger or get_compliance_logger())


def get_restore_executor(
    workspace_path: str | Path | None = None, logger: ComplianceLogger | None = None
) -> RestoreExecutor:
    """Create a :class:`RestoreExecutor` for ``workspace_path``.

    Parameters
    ----------
    workspace_path:
        Optional path to the workspace root. Defaults to ``GH_COPILOT_WORKSPACE``
        or ``."`` when not provided.
    logger:
        Pre-configured :class:`ComplianceLogger`. A new logger is created when
        omitted.
    """

    workspace = Path(workspace_path or os.getenv("GH_COPILOT_WORKSPACE", "."))
    return RestoreExecutor(workspace, logger or get_compliance_logger())


def schedule_backups() -> Path:
    """Convenience wrapper to schedule backups using the default system.

    Returns
    -------
    Path
        Location of the created backup file.
    """

    scheduler = get_backup_scheduler()
    return scheduler.schedule()


def restore_backup(path: str | Path) -> bool:
    """Restore a backup file with integrity verification.

    Parameters
    ----------
    path:
        Filesystem path to the backup file to restore.

    Returns
    -------
    bool
        ``True`` when restoration succeeds, ``False`` otherwise.
    """

    executor = get_restore_executor()
    return executor.restore(path)


# Re-export class for public consumers
UnifiedDisasterRecoverySystem = _UnifiedDisasterRecoverySystem

__all__ = [
    "UnifiedDisasterRecoverySystem",
    "BackupScheduler",
    "RestoreExecutor",
    "ComplianceLogger",
    "schedule_backups",
    "restore_backup",
    "log_backup_event",
    "get_compliance_logger",
    "get_backup_scheduler",
    "get_restore_executor",
]




# === BEGIN: AUTO-INJECTED DR HELPERS (safe to remove) ===
import sqlite3 as _sqlite3
from contextlib import contextmanager as _ctx


from datetime import datetime as _dt


def now_iso() -> str:
    return _dt.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


class AnalyticsLogger:
    def __init__(self, db_path: str = "analytics.db"):
        self.db_path = db_path
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with self._conn() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS events (event_time TEXT, level TEXT, event TEXT, details TEXT)"
            )

    @_ctx
    def _conn(self):
        con = _sqlite3.connect(self.db_path, timeout=10)
        try:
            yield con
            con.commit()
        finally:
            con.close()

    def log(self, level: str, event: str, details: str = "") -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO events VALUES (?,?,?,?)",
                (now_iso(), level, event, details),
            )


def _dr_create_backup(src: str, dest: str, logger: AnalyticsLogger | None = None) -> bool:
    import os as _os
    import shutil as _shutil

    try:
        if logger:
            logger.log("INFO", "backup_start", f"src={src} dest={dest}")
        if not _os.path.exists(src):
            raise FileNotFoundError(f"source not found: {src}")
        _os.makedirs(_os.path.dirname(dest) or ".", exist_ok=True)
        if _os.path.isdir(src):
            if _os.path.exists(dest):
                _shutil.rmtree(dest)
            _shutil.copytree(src, dest)
        else:
            _shutil.copy2(src, dest)
        if logger:
            logger.log("INFO", "backup_success", f"dest={dest}")
        return True
    except Exception as exc:  # noqa: BLE001
        if logger:
            logger.log(
                "ERROR",
                "backup_failure",
                f"{type(exc).__name__}: {exc}",
            )
        return False


def _dr_verify_backup(dest: str, logger: AnalyticsLogger | None = None) -> bool:
    import os as _os

    try:
        ok = _os.path.exists(dest) and (
            _os.path.isdir(dest) or _os.path.getsize(dest) >= 0
        )
        if logger:
            logger.log("INFO", "verify_result", f"dest={dest} ok={ok}")
        return ok
    except Exception as exc:  # noqa: BLE001
        if logger:
            logger.log(
                "ERROR",
                "verify_failure",
                f"{type(exc).__name__}: {exc}",
            )
        return False


def _dr_restore_from_backup(
    src: str, dest: str, logger: AnalyticsLogger | None = None
) -> bool:
    import os as _os
    import shutil as _shutil

    try:
        if logger:
            logger.log("INFO", "restore_start", f"src={src} dest={dest}")
        if not _os.path.exists(src):
            raise FileNotFoundError(f"backup not found: {src}")
        if _os.path.isdir(src):
            if _os.path.exists(dest):
                _shutil.rmtree(dest)
            _shutil.copytree(src, dest)
        else:
            _os.makedirs(_os.path.dirname(dest) or ".", exist_ok=True)
            _shutil.copy2(src, dest)
        if logger:
            logger.log("INFO", "restore_success", f"dest={dest}")
        return True
    except Exception as exc:  # noqa: BLE001
        if logger:
            logger.log(
                "ERROR",
                "restore_failure",
                f"{type(exc).__name__}: {exc}",
            )
        return False


def _dr_rollback(
    previous_state: str, dest: str, logger: AnalyticsLogger | None = None
) -> bool:
    return _dr_restore_from_backup(previous_state, dest, logger)


# === END: AUTO-INJECTED DR HELPERS ===

