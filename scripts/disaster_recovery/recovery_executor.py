"""Recovery execution helpers for the disaster recovery system."""

from __future__ import annotations

from pathlib import Path

from unified_disaster_recovery_system import UnifiedDisasterRecoverySystem


class RecoveryExecutor:
    """Wrapper around :class:`UnifiedDisasterRecoverySystem` restoration."""

    def __init__(self, workspace_root: str | None = None) -> None:
        self._system = UnifiedDisasterRecoverySystem(workspace_root)

    def run(self, backup_file: str | Path) -> bool:
        """Restore the provided backup file."""

        return self._system.restore_backup(backup_file)


__all__ = ["RecoveryExecutor"]

