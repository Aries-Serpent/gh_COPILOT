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
from datetime import timezone
from pathlib import Path
from sqlite3 import connect
from typing import Iterable, List

from tqdm import tqdm

from enterprise_modules.compliance import validate_enterprise_operation

from scripts.database.cross_database_sync_logger import log_sync_operation
from scripts.database.unified_database_initializer import initialize_database

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TRUNCATION_LIMIT = 200


def _copy_database(source: Path, target: Path) -> None:
    """Copy source database file to target using sqlite3 backup API."""
    validate_enterprise_operation()
    try:
        with connect(source) as source_conn, connect(target) as target_conn:
            source_conn.backup(target_conn)
        logger.info("Synchronized %s -> %s", source, target)
    except Exception as exc:
        logger.error("Failed to synchronize %s -> %s: %s", source, target, exc)


def synchronize_databases(
    master: Path,
    replicas: Iterable[Path],
    *,
    log_db: Path | None = None,
    timeout: int | None = None,
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
        start_dt = log_sync_operation(log_db, f"start_sync_from_{master.name}")
    else:
        start_dt = datetime.datetime.now(timezone.utc)
    start_time = time.time()
    logger.info("Starting synchronization at %s", datetime.datetime.fromtimestamp(start_time))

    replica_list = list(replicas)
    status = "SUCCESS"
    try:
        with tqdm(total=len(replica_list), desc="Syncing", unit="db", dynamic_ncols=True) as bar:
            for replica in replica_list:
                if timeout and time.time() - start_time > timeout:
                    logger.error("Synchronization timed out")
                    status = "TIMEOUT"
                    break
                _copy_database(master, replica)
                if log_db:
                    log_sync_operation(log_db, f"synchronized_{replica.name}", start_time=start_dt)
                etc = bar.format_dict.get("elapsed", 0) + bar.format_dict.get("remaining", 0)
                etc_time = datetime.datetime.fromtimestamp(start_time + etc)
                bar.set_postfix_str(f"ETC {etc_time.strftime('%H:%M:%S')}")
                bar.update(1)
    except Exception:
        status = "FAILURE"
        raise

    end_time = time.time()
    logger.info("Finished synchronization at %s", datetime.datetime.fromtimestamp(end_time))
    if log_db:
        op = f"timeout_sync_from_{master.name}" if status == "TIMEOUT" else f"completed_sync_from_{master.name}"
        log_sync_operation(log_db, op, status=status, start_time=start_dt)


def _load_database_names(list_file: Path) -> list[str]:
    """Return database names listed in the documentation file.

    Lines may include comments after a ``#`` which are ignored.
    """
    names: list[str] = []
    for line in list_file.read_text().splitlines():
        line = line.strip()
        if line.startswith("- "):
            name = line[2:]
            name = name.split("#", 1)[0].strip()
            if name:
                names.append(name)
    return names


class EnhancedDatabaseSyncScheduler:
    """Scheduler with detailed sync cycle logging."""

    def __init__(self, workspace_root: Path = Path("."), timeout: int | None = None) -> None:
        self.workspace_root = workspace_root.resolve()
        self.databases_dir = self.workspace_root / "databases"
        self.enterprise_db = self.databases_dir / "enterprise_assets.db"
        if not self.enterprise_db.exists():
            initialize_database(self.enterprise_db)
        self.master_db = self.databases_dir / "enterprise_assets.db"
        self.list_file = self.workspace_root / "documentation" / "CONSOLIDATED_DATABASE_LIST.md"
        self.timeout = timeout

    def execute_sync_cycle(self) -> None:
        """Execute a synchronization cycle with logging."""
        cycle_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        start_dt = log_sync_operation(self.enterprise_db, f"sync_cycle_start_{cycle_id}")
        try:
            db_names: List[str] = _load_database_names(self.list_file)
            replicas = [self.databases_dir / name for name in db_names if name != self.master_db.name]
            synchronize_databases(
                self.master_db,
                replicas,
                log_db=self.enterprise_db,
                timeout=self.timeout,
            )
            log_sync_operation(
                self.enterprise_db,
                f"sync_cycle_complete_{cycle_id}",
                start_time=start_dt,
            )
        except Exception as exc:
            log_sync_operation(
                self.enterprise_db,
                f"sync_cycle_failed_{cycle_id}_{format_exception_message(exc)}",
                status="FAILURE",
                start_time=start_dt,
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
        default="enterprise_assets.db",
        help="Master database filename",
    )
    parser.add_argument(
        "--target",
        type=str,
        help="Target database filename (overrides --master if specified)",
    )
    parser.add_argument(
        "--list-file",
        type=Path,
        default=Path("documentation") / "CONSOLIDATED_DATABASE_LIST.md",
        help="File listing databases to sync",
    )
    parser.add_argument(
        "--add-documentation-sync",
        action="append",
        type=Path,
        default=[],
        help="Additional files listing databases to sync",
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
    parser.add_argument(
        "--timeout",
        type=int,
        default=None,
        help="Abort sync if it runs longer than this many seconds",
    )

    args = parser.parse_args()

    workspace = args.workspace / "databases"
    master_name = args.target if args.target else args.master
    master_db = workspace / master_name
    list_path = args.list_file
    db_names = _load_database_names(list_path)
    for extra in args.add_documentation_sync:
        db_names.extend(_load_database_names(extra))
    # remove duplicates while preserving order
    seen = set()
    unique_names: list[str] = []
    for name in db_names:
        if name not in seen:
            seen.add(name)
            unique_names.append(name)
    db_names = unique_names
    replica_dbs = [workspace / name for name in db_names if name != master_name]

    log_db_path = workspace / args.log_db if args.log_db else None
    synchronize_databases(
        master_db,
        replica_dbs,
        log_db=log_db_path,
        timeout=args.timeout,
    )
