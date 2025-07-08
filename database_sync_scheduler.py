#!/usr/bin/env python3
"""Simple database synchronization scheduler.

This module synchronizes a set of SQLite databases by copying the
schema and data from a source database to one or more targets. It
is a minimal starting point to satisfy the planned cross-database
synchronization gap.
"""
from __future__ import annotations

import logging
import shutil
from pathlib import Path
from sqlite3 import Connection, connect
from typing import Iterable

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def _copy_database(source: Path, target: Path) -> None:
    """Copy source database file to target."""
    try:
        shutil.copy2(source, target)
        logger.info("Synchronized %s -> %s", source, target)
    except Exception as exc:
        logger.error("Failed to synchronize %s -> %s: %s", source, target, exc)


def synchronize_databases(master: Path, replicas: Iterable[Path]) -> None:
    """Synchronize replica databases with the master database."""
    for replica in replicas:
        _copy_database(master, replica)


if __name__ == "__main__":
    workspace = Path("./databases")
    master_db = workspace / "production.db"
    replica_dbs = [workspace / db for db in ("analytics.db", "staging.db")]
    synchronize_databases(master_db, replica_dbs)
