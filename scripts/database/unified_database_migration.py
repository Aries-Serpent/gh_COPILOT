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
from .complete_consolidation_orchestrator import create_external_backup
from scripts.validation.semantic_search_reference_validator import (
    chunk_anti_recursion_validation,
)

# Alias for legacy reference
validate_database_size = check_database_sizes


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

DEFAULT_SOURCES = [
    "analytics.db",
    "documentation.db",
    "template_completion.db",
]


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
    sources: list[str] = DEFAULT_SOURCES,
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
    chunk_anti_recursion_validation()
    db_dir = workspace / "databases"
    enterprise_db = db_dir / "enterprise_assets.db"
    initialize_database(enterprise_db)

    source_paths = [db_dir / name for name in sources if (db_dir / name).exists()]

    with tqdm(total=len(source_paths), desc="Migrating", unit="db") as bar:
        for src in source_paths:
            logger.info("Migrating %s", src.name)
            if compression_first:
                compress_database(src)
            create_external_backup(src, src.stem)
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
        default=DEFAULT_SOURCES,
        help="Database files to migrate",
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
