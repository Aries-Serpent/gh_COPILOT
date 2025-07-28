"""Autonomous backup manager with anti-recursion safeguards."""
from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path

from utils.cross_platform_paths import CrossPlatformPathManager
from utils.database_utils import get_validated_production_db_connection
from utils.validation_utils import validate_enterprise_environment
from tqdm import tqdm

__all__ = ["AutonomousBackupManager"]


class AutonomousBackupManager:
    """Create backups in the designated external directory."""

    FORBIDDEN_BACKUP_LOCATIONS = [
        os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT"),
        "C:/temp/",
        "./backup/",
    ]

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        validate_enterprise_environment()
        self.backup_root = Path(os.environ["GH_COPILOT_BACKUP_ROOT"]).resolve()
        if not self.validate_backup_location():
            raise EnvironmentError(f"Forbidden backup location: {self.backup_root}")
        self.backup_root.mkdir(parents=True, exist_ok=True)
        self.db_path = CrossPlatformPathManager.get_workspace_path() / "databases" / "production.db"

    def validate_backup_location(self) -> bool:
        """Ensure backup root doesn't match forbidden patterns."""
        path = str(self.backup_root).lower()
        for pattern in self.FORBIDDEN_BACKUP_LOCATIONS:
            if pattern and pattern.lower() in path:
                return False
        workspace = CrossPlatformPathManager.get_workspace_path().resolve()
        return workspace not in self.backup_root.parents and workspace != self.backup_root

    def create_backup(self, target: Path) -> Path:
        """Backup ``target`` to the backup root with validation."""
        target = Path(target).resolve()

        if self.backup_root in target.parents:
    def _validate_target(self, target: Path) -> None:
        workspace = CrossPlatformPathManager.get_workspace_path().resolve()
        backup_root = CrossPlatformPathManager.get_backup_root().resolve()
        if backup_root in target.parents:
            raise RuntimeError("Refusing to back up inside backup root")
        if workspace in target.parents:
            self.logger.debug("Backup of workspace subdir %s", target)
        if str(target).startswith("C:/temp"):
            raise RuntimeError("Forbidden backup location")

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
        files = [p for p in target.rglob("*")]
        with tqdm(files, desc=f"Backing up {target.name}", unit="file") as bar:
            for src in files:
                rel = src.relative_to(target)
                dst = dest / rel
                if src.is_dir():
                    dst.mkdir(parents=True, exist_ok=True)
                else:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                bar.update(1)

        self._record_backup(str(target), str(dest))
        self.logger.info("Backup created at %s", dest)
        return dest

    def _record_backup(self, source: str, destination: str) -> None:
        """Record backup details in production.db."""
        with get_validated_production_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS backup_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_path TEXT,
                    destination_path TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cur.execute(
                "INSERT INTO backup_history (source_path, destination_path) VALUES (?, ?)",
                (source, destination),
            )
            conn.commit()
