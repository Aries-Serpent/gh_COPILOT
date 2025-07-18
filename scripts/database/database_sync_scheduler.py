#!/usr/bin/env python3
"""Simple database synchronization scheduler.

This module synchronizes a set of SQLite databases by copying the
schema and data from a source database to one or more targets. It
is a minimal starting point to satisfy the planned cross-database
synchronization gap.
"""
from __future__ import annotations

import datetime
import logging
import time
from pathlib import Path
from sqlite3 import connect
from typing import Iterable, List

from .cross_database_sync_logger import log_sync_operation
from .unified_database_initializer import initialize_database

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


class EnhancedDatabaseSyncScheduler:
    """Scheduler with detailed sync cycle logging."""

    def __init__(self, workspace_root: Path = Path(".")) -> None:
        self.workspace_root = workspace_root.resolve()
        self.databases_dir = self.workspace_root / "databases"
        self.enterprise_db = self.databases_dir / "enterprise_assets.db"
        if not self.enterprise_db.exists():
            initialize_database(self.enterprise_db)
        self.master_db = self.databases_dir / "production.db"
        self.list_file = (
            self.workspace_root / "documentation" / "CONSOLIDATED_DATABASE_LIST.md"
        )

    def execute_sync_cycle(self) -> None:
        """Execute a synchronization cycle with logging."""
        cycle_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_sync_operation(self.enterprise_db, f"sync_cycle_start_{cycle_id}")
        try:
            db_names: List[str] = _load_database_names(self.list_file)
            replicas = [
                self.databases_dir / name
                for name in db_names
                if name != self.master_db.name
            ]
            synchronize_databases(
                self.master_db, replicas, log_db=self.enterprise_db
            )
            log_sync_operation(
                self.enterprise_db, f"sync_cycle_complete_{cycle_id}"
            )
        except Exception as exc:
            log_sync_operation(
                self.enterprise_db,
                f"sync_cycle_failed_{cycle_id}_{format_exception_message(exc)}",
            )
            raise

def format_exception_message(exc: Exception) -> str:
    """Format exception message with truncation."""
    exc_message = f"{type(exc).__name__}: {str(exc)}"
    return exc_message if len(exc_message) <= TRUNCATION_LIMIT else exc_message[:TRUNCATION_LIMIT] + "..."

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
    parser.add_argument(
        "--execute-cycle",
        action="store_true",
        help="Run a full synchronization cycle",
    )
    parser.add_argument(
        "--continuous-mode",
        action="store_true",
        help="Run synchronization cycles continuously",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=1800,
        help="Interval between cycles in continuous mode (seconds)",
    )

    args = parser.parse_args()

    workspace = args.workspace
    scheduler = EnhancedDatabaseSyncScheduler(workspace)

    if args.execute_cycle or args.continuous_mode:
        def run_cycle() -> None:
            scheduler.execute_sync_cycle()

        run_cycle()
        while args.continuous_mode:
            time.sleep(args.interval)
            run_cycle()
    else:
        databases_dir = workspace / "databases"
        master_db = databases_dir / args.master
        list_path = args.list_file
        db_names = _load_database_names(list_path)
        replica_dbs = [
            databases_dir / name for name in db_names if name != args.master
        ]
        log_db_path = databases_dir / args.log_db if args.log_db else None
        synchronize_databases(master_db, replica_dbs, log_db=log_db_path)
