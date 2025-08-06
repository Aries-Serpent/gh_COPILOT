"""Orchestrate disaster recovery operations.

This module provides a small wrapper that coordinates backup scheduling
and recovery execution. The implementation intentionally delegates the
heavy lifting to :class:`UnifiedDisasterRecoverySystem` while offering a
single entry point for other components such as session management or
dashboard utilities.

The logic is deliberately lightweight – full recovery behaviour will be
expanded in future iterations.
"""

from __future__ import annotations

from pathlib import Path

from enterprise_modules.compliance import pid_recursion_guard
from unified_disaster_recovery_system import UnifiedDisasterRecoverySystem


class DisasterRecoveryOrchestrator:
    """Coordinate backup scheduling and recovery execution."""

    @pid_recursion_guard
    def __init__(self, workspace_root: str | None = None) -> None:
        self._system = UnifiedDisasterRecoverySystem(workspace_root)

    def run_backup_cycle(self) -> Path:
        """Create a timestamped backup using the unified system."""

        return self._system.schedule_backups()

    def run_recovery_cycle(self, backup_file: str | Path) -> bool:
        """Restore the provided backup file."""

        return self._system.restore_backup(backup_file)


__all__ = ["DisasterRecoveryOrchestrator"]

