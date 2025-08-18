#!/usr/bin/env python3
"""
UnifiedDatabaseMigration - Enterprise Utility Script
Generated: 2025-07-22 09:08:49 | Author: mbaetiong

Enterprise Standards Compliance:
- Flake8/PEP 8 Compliant
- Emoji-free code (text-based indicators only)
- Visual processing indicators

Roles: [Primary] ⚡ Energy: 5 | Physics: Path🛤️ Fields🔄 Patterns👁️ Redundancy🔀 Balance⚖️
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

from tqdm import tqdm

from .cross_database_sync_logger import log_sync_operation
from .database_consolidation_migration import consolidate_databases
from .size_compliance_checker import check_database_sizes
from .unified_database_initializer import initialize_database
from .complete_consolidation_orchestrator import create_external_backup
from utils.logging_utils import setup_enterprise_logging
from scripts.validation.semantic_search_reference_validator import (
    chunk_anti_recursion_validation,
)
from secondary_copilot_validator import SecondaryCopilotValidator

# Alias for legacy reference
validate_database_size_reference = check_database_sizes


def _compress_database(db_path: Path) -> None:
    """Compress the SQLite database in-place.

    Parameters
    ----------
    db_path:
        Path to the database file to compress.
    """
    orig_size = db_path.stat().st_size
    tmp_path = db_path.with_suffix(".tmp")
    with sqlite3.connect(db_path) as conn:
        conn.execute(f"VACUUM INTO '{tmp_path}'")
    if tmp_path.exists():
        new_size = tmp_path.stat().st_size
        if new_size <= orig_size:
            tmp_path.replace(db_path)
        else:
            tmp_path.unlink()
    with sqlite3.connect(db_path) as conn:
        conn.execute("REINDEX")
        conn.execute("ANALYZE")
        conn.commit()


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


def compress_database(db_path: Path) -> None:
    """Compress ``db_path`` in place using VACUUM and ANALYZE."""
    if not db_path.exists():
        return
    with sqlite3.connect(db_path) as conn:
        conn.execute("VACUUM")
        conn.execute("REINDEX")
        conn.execute("ANALYZE")
        conn.commit()


def validate_database_size(databases_dir: Path, limit_mb: float = 99.9) -> None:
    """Raise ``RuntimeError`` if any database exceeds ``limit_mb``."""
    sizes = check_database_sizes(databases_dir, threshold_mb=limit_mb)
    oversized = {name: size for name, size in sizes.items() if size > limit_mb}
    if oversized:
        details = ", ".join(f"{name}: {size:.2f} MB" for name, size in oversized.items())
        raise RuntimeError(f"Database size limit exceeded: {details}")


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
    chunk_anti_recursion_validation()
    db_dir = workspace / "databases"
    enterprise_db = db_dir / "enterprise_assets.db"
    initialize_database(enterprise_db)
    migration_start = datetime.now(timezone.utc)
    log_sync_operation(enterprise_db, "migration_started", start_time=migration_start)

    if sources is None:
        list_file = workspace / DATABASE_LIST_FILE
        sources = _load_database_names(list_file)

    source_paths = [db_dir / name for name in sources if (db_dir / name).exists()]

    with tqdm(total=len(source_paths), desc="Migrating", unit="db") as bar:
        for src in source_paths:
            logger.info("Migrating %s", src.name)
            if compression_first:
                compress_database(src)
            create_external_backup(src, src.stem)
            start_dt = log_sync_operation(enterprise_db, f"start_migrate_{src.name}", start_time=None)
            consolidate_databases(enterprise_db, [src])
            log_sync_operation(enterprise_db, f"completed_migrate_{src.name}", start_time=start_dt)
            _compress_database(enterprise_db)
            bar.update(1)
            if monitor_size:
                sizes = check_database_sizes(db_dir)
                if any(size > 99.9 for size in sizes.values()):
                    raise RuntimeError("Database size limit exceeded")

    if monitor_size:
        sizes = check_database_sizes(db_dir)
        if any(size > 99.9 for size in sizes.values()):
            raise RuntimeError("Database size limit exceeded")

    log_sync_operation(
        enterprise_db,
        "migration_complete",
        start_time=migration_start,
    )

    # DUAL COPILOT PATTERN: secondary validation
    validator = SecondaryCopilotValidator(logger)
    validator.validate_corrections([__file__])


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
    setup_enterprise_logging()
    run_migration(
        args.workspace,
        args.sources,
        compression_first=args.compression_first,
        monitor_size=args.monitor_size,
    )
