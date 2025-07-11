#!/usr/bin/env python3
"""Unified database management utilities."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Iterable, Tuple

logger = logging.getLogger(__name__)

DATABASE_LIST_FILE = Path("documentation") / "DATABASE_LIST.md"


class UnifiedDatabaseManager:
    """Manage expected databases for the workspace."""

    def __init__(self, workspace_root: str = ".") -> None:
        self.workspace_root = Path(workspace_root)
        self.databases_dir = self.workspace_root / "databases"

    def _load_expected_names(self) -> list[str]:
        names: list[str] = []
        try:
            for line in DATABASE_LIST_FILE.read_text().splitlines():
                line = line.strip()
                if line.startswith("- "):
                    name = line[2:].strip()
                    if name:
                        names.append(name)
        except FileNotFoundError:
            logger.error("Database list file not found: %s", DATABASE_LIST_FILE)
        except OSError as e:
            logger.error("Error reading database list file %s: %s", DATABASE_LIST_FILE, e)
        return names

    def verify_expected_databases(self) -> Tuple[bool, list[str]]:
        """Return whether all expected databases exist and any missing ones."""
        expected = self._load_expected_names()
        missing = [name for name in expected if not (
            self.databases_dir / name).exists()]
        return len(missing) == 0, missing

def _backup_database(source: Path, target: Path) -> None:
    """Copy source SQLite database to target using backup API."""
    with sqlite3.connect(source) as src, sqlite3.connect(target) as dest:
        src.backup(dest)
        logger.info("Synchronized %s -> %s", source, target)


def synchronize_databases(master: Path, replicas: Iterable[Path]) -> None:
    """Synchronize replica databases with the master database."""
    for replica in replicas:
        _backup_database(master, replica)


if __name__ == "__main__":
    mgr = UnifiedDatabaseManager(Path.cwd())
    ok, missing_dbs = mgr.verify_expected_databases()
    if not ok:
        print("Missing databases:", ", ".join(missing_dbs))
