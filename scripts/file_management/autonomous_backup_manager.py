"""Autonomous backup manager placeholder."""
from __future__ import annotations

import logging
import shutil
from pathlib import Path

from utils.cross_platform_paths import CrossPlatformPathManager

__all__ = ["AutonomousBackupManager"]


class AutonomousBackupManager:
    """Create backups in the designated external directory."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.backup_root = CrossPlatformPathManager.get_backup_root() / "temp" / "gh_COPILOT_Backups"
        self.backup_root.mkdir(parents=True, exist_ok=True)

    def create_backup(self, target: Path) -> Path:
        """Backup the target directory to the backup root."""
        dest = self.backup_root / target.name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(target, dest)
        self.logger.info("Backup created at %s", dest)
        return dest
