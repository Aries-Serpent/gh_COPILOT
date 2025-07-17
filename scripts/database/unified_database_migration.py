#!/usr/bin/env python3
"""Orchestrate migration of assets into enterprise_assets.db."""

from __future__ import annotations

import logging
from pathlib import Path

from tqdm import tqdm

from .cross_database_sync_logger import log_sync_operation
from .database_consolidation_migration import consolidate_databases
from .size_compliance_checker import check_database_sizes
from .unified_database_initializer import initialize_database

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


def run_migration(workspace: Path, sources: list[str] = DEFAULT_SOURCES) -> None:
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

    source_paths = [db_dir / name for name in sources if (db_dir / name).exists()]

    with tqdm(total=len(source_paths), desc="Migrating", unit="db") as bar:
        for src in source_paths:
            logger.info("Migrating %s", src.name)
            log_sync_operation(enterprise_db, f"start_migrate_{src.name}")
            consolidate_databases(enterprise_db, [src])
            log_sync_operation(enterprise_db, f"completed_migrate_{src.name}")
            bar.update(1)
            if not check_database_sizes(db_dir):
                raise RuntimeError("Database size limit exceeded")

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

    args = parser.parse_args()
    run_migration(args.workspace, args.sources)
