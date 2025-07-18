#!/usr/bin/env python3
"""Complete database consolidation orchestrator."""

from __future__ import annotations

import csv
import logging
import os
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Iterable, List

import py7zr
from tqdm import tqdm

from scripts.continuous_operation_orchestrator import \
    validate_enterprise_operation

from .database_migration_corrector import DatabaseMigrationCorrector
from .size_compliance_checker import check_database_sizes
from .unified_database_initializer import initialize_database

logger = logging.getLogger(__name__)


def export_table_to_7z(
    db_path: Path, table: str, dest_dir: Path, level: int = 5
) -> Path:
    """Export ``table`` from ``db_path`` to ``dest_dir`` as a 7z archive.

    Parameters
    ----------
    db_path:
        Path to the database containing ``table``.
    table:
        Table name to export.
    dest_dir:
        Directory where the resulting archive will be created.
    level:
        Compression level passed to ``py7zr``.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    archive_path = dest_dir / f"{db_path.stem}_{table}.7z"
    with sqlite3.connect(db_path) as conn, tempfile.NamedTemporaryFile(
        "w", delete=False, suffix=f"_{table}.csv"
    ) as tmp:
        writer = csv.writer(tmp)
        cur = conn.execute(f"SELECT * FROM {table}")
        writer.writerow([d[0] for d in cur.description])
        writer.writerows(cur.fetchall())
        tmp_path = Path(tmp.name)
    with py7zr.SevenZipFile(
        archive_path, mode="w", compression_level=level
    ) as zf:
        zf.write(tmp_path, arcname=tmp_path.name)
    tmp_path.unlink()
    logger.info("Compressed %s.%s to %s", db_path.name, table, archive_path)
    return archive_path


def compress_large_tables(
    db_path: Path, analysis: dict, threshold: int = 50000, *, level: int = 5
) -> List[Path]:
    """Compress tables with a row count greater than ``threshold``.

    Parameters
    ----------
    db_path:
        Database being analyzed.
    analysis:
        Table structure analysis from ``DatabaseMigrationCorrector``.
    threshold:
        Minimum row count required to trigger compression.
    level:
        Compression level to use when creating the archive.
    """
    archives: List[Path] = []
    for table in analysis.get("tables", []):
        if table.get("record_count", 0) > threshold:
            archives.append(
                export_table_to_7z(
                    db_path,
                    table["name"],
                    Path("archives/table_exports"),
                    level,
                )
            )
    return archives


def migrate_and_compress(
    workspace: Path, sources: Iterable[str], *, level: int = 5
) -> None:
    """Migrate ``sources`` into enterprise_assets.db with compression.

    Parameters
    ----------
    workspace:
        Workspace root containing the databases directory.
    sources:
        Iterable of database file names to consolidate.
    level:
        Compression level used when exporting large tables.
    """
    validate_enterprise_operation()
    db_dir = workspace / "databases"
    enterprise_db = db_dir / "enterprise_assets.db"
    initialize_database(enterprise_db)

    total = len(sources)
    start = perf_counter()
    with tqdm(total=total, desc="Consolidating", unit="db") as bar:
        for idx, name in enumerate(sources, 1):
            src = db_dir / name
            if not src.exists():
                bar.update(1)
                continue
            migrator = DatabaseMigrationCorrector()
            migrator.workspace_root = workspace
            migrator.source_db = src
            migrator.target_db = enterprise_db
            migrator.migration_report = {"errors": []}
            migrator.migrate_database_content()
            analysis = migrator.analyze_database_structure(enterprise_db)
            compress_large_tables(enterprise_db, analysis, level=level)
            elapsed = perf_counter() - start
            remaining = (total - idx) * (elapsed / idx)
            bar.set_postfix(ETC=f"{remaining:.1f}s")
            bar.update(1)

    if not check_database_sizes(db_dir):
        raise RuntimeError("Database size limit exceeded")
    logger.info("Consolidation complete")


if __name__ == "__main__":
    import argparse

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    parser = argparse.ArgumentParser(
        description="Consolidate databases with optional table compression"
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd())),
        help="Workspace root",
    )
    parser.add_argument(
        "--compression-level",
        type=int,
        default=5,
        help="Compression level for 7z archives",
    )

    args = parser.parse_args()

    migrate_and_compress(
        args.workspace,
        ["analytics.db", "documentation.db", "template_completion.db"],
        level=args.compression_level,
    )
