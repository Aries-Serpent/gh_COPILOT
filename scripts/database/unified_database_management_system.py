#!/usr/bin/env python3
"""Unified database management utilities."""

from __future__ import annotations

import logging
import os
import sqlite3
from pathlib import Path
from typing import Iterable, Tuple
import datetime

from tqdm import tqdm

from enterprise_modules.compliance import validate_enterprise_operation
from scripts.database.cross_database_sync_logger import log_sync_operation

logger = logging.getLogger(__name__)

DATABASE_LIST_FILE = Path("documentation") / "CONSOLIDATED_DATABASE_LIST.md"
WORKSPACE_ENV_VAR = "GH_COPILOT_WORKSPACE"


def parse_comment(text: str) -> str:
    """Return ``text`` with trailing comment or annotation removed."""

    text = text.split("#", 1)[0]
    # remove markdown style parentheses notes e.g. "*(archived)*"
    if "*(" in text:
        text = text.split("*(", 1)[0]
    return text.strip()


class UnifiedDatabaseManager:
    """Manage expected databases for the workspace."""

    WORKSPACE_ENV_VAR = "GH_COPILOT_WORKSPACE"

    def __init__(self, workspace_root: str = ".") -> None:
        workspace = os.getenv(WORKSPACE_ENV_VAR, workspace_root)
        self.workspace_root = Path(workspace)
        self.databases_dir = self.workspace_root / "databases"

    def _load_expected_names(self) -> list[str]:
        """Return database names from the consolidated list.

        Lines may include comments after a ``#`` which are ignored.
        """
        names: list[str] = []
        for line in DATABASE_LIST_FILE.read_text().splitlines():
            line = line.strip()
            if line.startswith("- "):
                name = parse_comment(line[2:])
                if name:
                    names.append(name)
        return names

    def verify_expected_databases(self) -> Tuple[bool, list[str]]:
        """Return whether all expected databases exist and any missing ones."""
        expected = self._load_expected_names()
        missing = [name for name in expected if not (self.databases_dir / name).exists()]
        return len(missing) == 0, missing


def _backup_database(source: Path, target: Path, log_db: Path | None = None) -> None:
    """Copy source SQLite database to target using backup API."""
    validate_enterprise_operation()
    start_dt = datetime.datetime.now(datetime.timezone.utc)
    with sqlite3.connect(source) as src, sqlite3.connect(target) as dest, tqdm(
        total=1, desc=f"Backup {source.name}", unit="db"
    ) as bar:
        src.backup(dest)
        bar.update(1)
    logger.info("Synchronized %s -> %s", source, target)
    if log_db:
        log_sync_operation(
            log_db,
            f"backup_{source.name}_to_{target.name}",
            start_time=start_dt,
        )


def synchronize_databases(master: Path, replicas: Iterable[Path], log_db: Path | None = None) -> None:
    """Synchronize replica databases with the master database."""
    validate_enterprise_operation()
    replica_list = list(replicas)
    with tqdm(total=len(replica_list), desc="Synchronizing", unit="db") as bar:
        for replica in replica_list:
            _backup_database(master, replica, log_db=log_db)
            bar.update(1)


if __name__ == "__main__":
    mgr = UnifiedDatabaseManager(str(Path.cwd()))
    ok, missing_dbs = mgr.verify_expected_databases()
    if not ok:
        print("Missing databases:", ", ".join(missing_dbs))
