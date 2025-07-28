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

        backup_root = CrossPlatformPathManager.get_backup_root().resolve()
        target_dir = Path(target_dir).resolve()
        if backup_root in target_dir.parents:
            raise RuntimeError("Refusing to organize files inside backup root")
        if self.workspace not in target_dir.parents and target_dir != self.workspace:
            raise RuntimeError("Target directory must be within workspace")

        paths = [p for p in target_dir.iterdir() if p.is_file()]
        with tqdm(paths, desc="Organizing", unit="file") as bar:
            for f in bar:
                bar.set_postfix(file=f.name)
                dest = self._get_destination(f)
                dest.parent.mkdir(parents=True, exist_ok=True)
                try:
                    f.rename(dest)
                except Exception as exc:  # noqa: BLE001
                    self.logger.error("Failed moving %s: %s", f, exc)
                self._record_file(dest)
        self.logger.info("Organized %d files", len(paths))

    def _record_file(self, path: Path) -> None:
        """Record file location in ``production.db`` if table exists."""
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT OR IGNORE INTO file_system_mappings (path) VALUES (?)",
                    (str(path),),
                )
        except sqlite3.OperationalError:
            self.logger.debug("file_system_mappings table missing")

    def _get_destination(self, path: Path) -> Path:
        """Determine destination path using database-driven classification.

        The method first looks up ``enhanced_script_tracking`` for the given
        ``script_path`` to retrieve ``script_type`` and ``functionality_category``.
        If the path is not tracked, it falls back to ``functional_components``
        using the filename stem as ``component_name``. When no data exists,
        ``script_type`` defaults to ``"misc"``.
        """

        script_type = "misc"
        category: str | None = None
        with self.conn:
            cur = self.conn.execute(
                "SELECT script_type, functionality_category FROM enhanced_script_tracking WHERE script_path=?",
                (str(path),),
            )
            row = cur.fetchone()
            if row:
                script_type = row[0]
                category = row[1]
            else:
                cur = self.conn.execute(
                    "SELECT component_type FROM functional_components WHERE component_name=?",
                    (path.stem,),
                )
                comp = cur.fetchone()
                if comp:
                    script_type = comp[0]

        parts = [self.workspace, "organized"]
        if category:
            parts.append(category)
        parts.append(script_type)
        dest_dir = Path(*parts)
        return dest_dir / path.name
