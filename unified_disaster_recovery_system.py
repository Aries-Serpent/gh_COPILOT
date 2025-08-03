"""Unified Disaster Recovery System public interface.

This module exposes the :class:`UnifiedDisasterRecoverySystem` class along with
helper utilities for scheduling backups and logging compliance events. The
actual implementation lives in ``scripts.utilities.unified_disaster_recovery_system``
but we keep this thin wrapper so downstream code can simply import from
``unified_disaster_recovery_system``.
"""

from __future__ import annotations

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
    UnifiedDisasterRecoverySystem as _UnifiedDisasterRecoverySystem,
)


def schedule_backups() -> None:
    """Convenience wrapper to schedule backups using the default system."""

    system = _UnifiedDisasterRecoverySystem()
    system.schedule_backups()


# Re-export class for public consumers
UnifiedDisasterRecoverySystem = _UnifiedDisasterRecoverySystem

__all__ = ["UnifiedDisasterRecoverySystem", "schedule_backups", "log_backup_event"]

