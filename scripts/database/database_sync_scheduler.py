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

from .cross_database_sync_logger import log_sync_operation

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def _copy_database(source: Path, target: Path) -> None:
    """Copy source database file to target using sqlite3 backup API."""
    try:
        with connect(source) as source_conn, connect(target) as target_conn:
            source_conn.backup(target_conn)
        logger.info("Synchronized %s -> %s", source, target)
    except Exception as exc:
        logger.error("Failed to synchronize %s -> %s: %s", source, target, exc)


def synchronize_databases(
    master: Path, replicas: Iterable[Path], log_db: Path | None = None
) -> None:
    """Synchronize replica databases with the master database.

    Parameters
    ----------
    master:
        Source database to copy from.
    replicas:
        Iterable of replica database paths.
    log_db:
        Optional path to ``enterprise_assets.db`` for audit logging.
    """
    if log_db:
        log_sync_operation(log_db, f"start_sync_from_{master.name}")
    for replica in replicas:
        _copy_database(master, replica)
        if log_db:
            log_sync_operation(log_db, f"synchronized_{replica.name}")
    if log_db:
        log_sync_operation(log_db, f"completed_sync_from_{master.name}")


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
    import argparse

    parser = argparse.ArgumentParser(description="Synchronize databases")
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path(".").resolve(),
        help="Workspace root containing databases/",
    )
    parser.add_argument(
        "--master",
        type=str,
        default="production.db",
        help="Master database filename",
    )
    parser.add_argument(
        "--list-file",
        type=Path,
        default=Path("documentation") / "CONSOLIDATED_DATABASE_LIST.md",
        help="File listing databases to sync",
    )
    parser.add_argument(
        "--log-db",
        type=str,
        default="enterprise_assets.db",
        help="Database filename used for logging",
    )

    args = parser.parse_args()

    workspace = args.workspace / "databases"
    master_db = workspace / args.master
    list_path = args.list_file
    db_names = _load_database_names(list_path)
    replica_dbs = [workspace / name for name in db_names if name != args.master]

    log_db_path = workspace / args.log_db if args.log_db else None
    synchronize_databases(master_db, replica_dbs, log_db=log_db_path)
