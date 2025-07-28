"""Autonomous backup manager with anti-recursion safeguards."""
from __future__ import annotations

import logging
import shutil
from pathlib import Path

from utils.cross_platform_paths import CrossPlatformPathManager
from utils.validation_utils import validate_enterprise_environment

__all__ = ["AutonomousBackupManager"]


class AutonomousBackupManager:
    """Create backups in the designated external directory."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        validate_enterprise_environment()
        self.backup_root = CrossPlatformPathManager.get_backup_root() / "temp" / "gh_COPILOT_Backups"
        self.backup_root.mkdir(parents=True, exist_ok=True)

    def _validate_target(self, target: Path) -> None:
        workspace = CrossPlatformPathManager.get_workspace_path().resolve()
        backup_root = CrossPlatformPathManager.get_backup_root().resolve()
        if backup_root in target.parents:
            raise RuntimeError("Refusing to back up inside backup root")
        if workspace in target.parents:
            self.logger.debug("Backup of workspace subdir %s", target)
        if str(target).startswith("C:/temp"):
            raise RuntimeError("Forbidden backup location")

    def create_backup(self, target: Path) -> Path:
        """Backup ``target`` to the backup root with validation."""
        target = Path(target).resolve()
        self._validate_target(target)

        dest = self.backup_root / target.name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(target, dest)
        self.logger.info("Backup created at %s", dest)
        return dest
