#!/usr/bin/env python3
"""Orchestrate migration of assets into enterprise_assets.db."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

from tqdm import tqdm

from .cross_database_sync_logger import log_sync_operation
from .database_consolidation_migration import consolidate_databases
from .size_compliance_checker import check_database_sizes
from .unified_database_initializer import initialize_database


def _compress_database(db_path: Path) -> None:
    """Compress the SQLite database in-place.

    Parameters
    ----------
    db_path:
        Path to the database file to compress.
    """
    with sqlite3.connect(db_path) as conn:
        conn.execute("VACUUM")
        conn.execute("REINDEX")
        conn.execute("ANALYZE")
        conn.commit()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

DATABASE_LIST_FILE = Path("documentation") / "CONSOLIDATED_DATABASE_LIST.md"


def _load_database_names(list_file: Path) -> list[str]:
    """Return database names listed in ``list_file``.

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


def validate_database_size(databases_dir: Path) -> None:
    """Check size compliance for databases in ``databases_dir``."""
    check_database_sizes(databases_dir)


def compress_database(db_path: Path) -> None:
    """Compress ``db_path`` in place using VACUUM and ANALYZE."""
    if not db_path.exists():
        return
    with sqlite3.connect(db_path) as conn:
        conn.execute("VACUUM")
        conn.execute("REINDEX")
        conn.execute("ANALYZE")
        conn.commit()


def run_migration(
    workspace: Path,
    sources: list[str] | None = None,
    *,
    compression_first: bool = False,
    monitor_size: bool = False,
) -> None:
    """Migrate the given database ``sources`` into ``enterprise_assets.db``.

    Parameters
    ----------
    workspace:
        Workspace root containing the ``databases`` directory.
    sources:
        List of database file names to migrate.
    """
    db_dir = workspace / "databases"
    enterprise_db = db_dir / "enterprise_assets.db"
    initialize_database(enterprise_db)

    if sources is None:
        list_file = workspace / DATABASE_LIST_FILE
        sources = _load_database_names(list_file)

    source_paths = [db_dir / name for name in sources if (db_dir / name).exists()]

    with tqdm(total=len(source_paths), desc="Migrating", unit="db") as bar:
        for src in source_paths:
            logger.info("Migrating %s", src.name)
            if compression_first:
                compress_database(src)
            log_sync_operation(enterprise_db, f"start_migrate_{src.name}")
            consolidate_databases(enterprise_db, [src])
            log_sync_operation(enterprise_db, f"completed_migrate_{src.name}")
            _compress_database(enterprise_db)
            bar.update(1)
            if monitor_size:
                validate_database_size(db_dir)

    if monitor_size:
        validate_database_size(db_dir)

    log_sync_operation(enterprise_db, "migration_complete")
    logger.info("Migration process completed")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run unified database migration")
    parser.add_argument(
        "--workspace",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Workspace root",
    )
    parser.add_argument(
        "sources",
        nargs="*",
        default=None,
        help="Database files to migrate (defaults to list from documentation)",
    )
    parser.add_argument(
        "--compression-first",
        action="store_true",
        help="Compress databases before migration",
    )
    parser.add_argument(
        "--monitor-size",
        action="store_true",
        help="Check size compliance during migration",
    )

    args = parser.parse_args()
    run_migration(
        args.workspace,
        args.sources,
        compression_first=args.compression_first,
        monitor_size=args.monitor_size,
    )
