"""Backup scheduling utilities for the disaster recovery system."""

from __future__ import annotations

from pathlib import Path

from unified_disaster_recovery_system import UnifiedDisasterRecoverySystem


class BackupScheduler:
    """Wrapper around :class:`UnifiedDisasterRecoverySystem` scheduling."""

    def __init__(self, workspace_root: str | None = None) -> None:
        self._system = UnifiedDisasterRecoverySystem(workspace_root)

    def run(self) -> Path:
        """Create a new backup and return the resulting file path."""

        return self._system.schedule_backups()


__all__ = ["BackupScheduler"]

