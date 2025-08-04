"""Unified Disaster Recovery System public interface.

This module exposes the :class:`UnifiedDisasterRecoverySystem` class along with
helper utilities for scheduling backups and logging compliance events. The
actual implementation lives in ``scripts.utilities.unified_disaster_recovery_system``
but we keep this thin wrapper so downstream code can simply import from
``unified_disaster_recovery_system``.
"""

from __future__ import annotations

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


def schedule_backups() -> Path:
    """Convenience wrapper to schedule backups using the default system.

    Returns
    -------
    Path
        Location of the created backup file.
    """

    system = _UnifiedDisasterRecoverySystem()
    return system.schedule_backups()


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

    system = _UnifiedDisasterRecoverySystem()
    return system.restore_backup(path)


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
]

