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

