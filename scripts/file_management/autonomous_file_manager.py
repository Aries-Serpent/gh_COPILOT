"""Autonomous file manager with database-driven organization.

This module implements the core AutonomousFileManager class which uses
``production.db`` to determine optimal file locations. It enforces
anti-recursion rules by validating paths against the workspace and backup
directories. Visual progress indicators are provided with ``tqdm``.
"""
from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

from tqdm import tqdm

from utils.cross_platform_paths import CrossPlatformPathManager
from utils.validation_utils import validate_enterprise_environment

__all__ = ["AutonomousFileManager"]


class AutonomousFileManager:
    """Database-driven file organizer with anti-recursion enforcement."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.logger = logging.getLogger(__name__)
        self.workspace = CrossPlatformPathManager.get_workspace_path()
        self.backup_root = CrossPlatformPathManager.get_backup_root().resolve()
        validate_enterprise_environment()

    @staticmethod
    def _is_within(path: Path, parent: Path) -> bool:
        try:
            path.resolve().relative_to(parent)
            return True
        except ValueError:
            return False

    def organize_files(self, target_dir: Path) -> None:
        """Organize files based on database patterns.

        Parameters
        ----------
        target_dir:
            Directory containing files to organize. Must be inside the
            workspace and outside the backup root.
        """

        target_dir = Path(target_dir).resolve()
        if self._is_within(target_dir, self.backup_root):
            raise RuntimeError("Refusing to organize files inside backup root")
        if not self._is_within(target_dir, self.workspace) and target_dir != self.workspace:
            raise RuntimeError("Target directory must be within workspace")

        files = [p for p in target_dir.iterdir() if p.is_file()]
        with tqdm(files, desc="Organizing", unit="file") as bar:
            for f in bar:
                bar.set_postfix(file=f.name)
                self._record_file(f)
        self.logger.info("Organized %d files", len(files))

    def _record_file(self, path: Path) -> None:
        """Move file to organized folder and update database."""
        cur = self.conn.execute(
            "SELECT functionality_category, script_type FROM enhanced_script_tracking WHERE script_path=?",
            (str(path),),
        )
        row = cur.fetchone()
        category = row["functionality_category"] if row else "misc"
        script_type = row["script_type"] if row else "general"

        dest = self.workspace / "organized" / category / script_type / path.name
        if self._is_within(dest, self.backup_root):
            raise RuntimeError("Destination inside backup root")

        dest.parent.mkdir(parents=True, exist_ok=True)
        if path.resolve() != dest.resolve():
            path.rename(dest)
            self.logger.info("Moved %s to %s", path, dest)

        with self.conn:
            self.conn.execute(
                "UPDATE enhanced_script_tracking SET script_path=?, last_updated=CURRENT_TIMESTAMP WHERE script_path=?",
                (str(dest), str(path)),
            )
            self.conn.execute(
                "INSERT OR IGNORE INTO functional_components (component_name, component_type) VALUES (?, ?)",
                (dest.name, script_type),
            )
            self.conn.execute(
                "INSERT OR IGNORE INTO file_system_mapping (file_path) VALUES (?)",
                (str(dest),),
            )
