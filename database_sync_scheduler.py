#!/usr/bin/env python3
"""Simple database synchronization scheduler.

This module synchronizes a set of SQLite databases by copying the
schema and data from a source database to one or more targets. It
is a minimal starting point to satisfy the planned cross-database
synchronization gap.
"""
from __future__ import annotations

import logging
from pathlib import Path
from sqlite3 import connect
from typing import Iterable

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def _copy_database(source: Path, target: Path) -> None:
    """Copy source database file to target using sqlite3 backup API."""
    try:
        with connect(source) as source_conn, connect(target) as target_conn:
            source_conn.backup(target_conn)
        logger.info("Synchronized %s -> %s", source, target)
    except Exception as exc:
        logger.error("Failed to synchronize %s -> %s: %s", source, target, exc)


def synchronize_databases(master: Path, replicas: Iterable[Path]) -> None:
    """Synchronize replica databases with the master database."""
    for replica in replicas:
        _copy_database(master, replica)


def _load_database_names(list_file: Path) -> list[str]:
    """Return database names listed in the documentation file."""
    names: list[str] = []
    for line in list_file.read_text().splitlines():
        line = line.strip()
        if line.startswith("- "):
            name = line[2:].strip()
            if name:
                names.append(name)
    return names


if __name__ == "__main__":
    workspace = Path("./databases")
    master_db = workspace / "production.db"
    list_path = Path("documentation") / "DATABASE_LIST.md"
    db_names = _load_database_names(list_path)
    replica_dbs = [
        workspace / name for name in db_names if name != "production.db"
    ]
    synchronize_databases(master_db, replica_dbs)
