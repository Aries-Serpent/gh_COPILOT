#!/usr/bin/env python3
"""UnifiedDisasterRecoverySystem - Enterprise Utility Script."""

from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

__all__ = ["UnifiedDisasterRecoverySystem", "main"]

TEXT_INDICATORS = {
    "start": "[START]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
    "info": "[INFO]",
}


class UnifiedDisasterRecoverySystem:
    """Perform simple disaster recovery from backups."""

    def __init__(self, workspace_path: Optional[str] = None) -> None:
        self.workspace_path = Path(workspace_path or os.getenv("GH_COPILOT_WORKSPACE", "."))
        self.logger = logging.getLogger(self.__class__.__name__)

    def perform_recovery(self) -> bool:
        """Restore files from ``GH_COPILOT_BACKUP_ROOT``."""
        start_time = datetime.now()
        backup_root = Path(os.getenv("GH_COPILOT_BACKUP_ROOT", "/tmp/gh_COPILOT_Backups")).resolve()
        workspace = self.workspace_path.resolve()

        if workspace in backup_root.parents or backup_root == workspace:
            self.logger.error(
                "%s Backup root %s resides within workspace %s",
                TEXT_INDICATORS["error"],
                backup_root,
                workspace,
            )
            return False

        source = backup_root / "production_backup"
        restore_dir = self.workspace_path / "restored"
        restore_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("%s Starting disaster recovery from %s", TEXT_INDICATORS["start"], source)

        if not source.exists():
            self.logger.error("%s Backup source missing: %s", TEXT_INDICATORS["error"], source)
            return False

        for item in source.glob("*"):
            try:
                shutil.copy2(item, restore_dir / item.name)
                self.logger.info("%s Restored %s", TEXT_INDICATORS["info"], item.name)
            except OSError as exc:
                self.logger.error("%s Failed to restore %s: %s", TEXT_INDICATORS["error"], item.name, exc)
                return False

        duration = (datetime.now() - start_time).total_seconds()
        self.logger.info("%s Disaster recovery completed in %.1fs", TEXT_INDICATORS["success"], duration)
        return True


def main() -> int:
    system = UnifiedDisasterRecoverySystem()
    return 0 if system.perform_recovery() else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
