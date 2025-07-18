#!/usr/bin/env python3
"""Complete database consolidation orchestrator."""

from __future__ import annotations

import csv
import logging
import os
import shutil
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Iterable, List, Optional

import py7zr
from tqdm import tqdm

from scripts.continuous_operation_orchestrator import \
    validate_enterprise_operation

from .database_migration_corrector import DatabaseMigrationCorrector
from .size_compliance_checker import check_database_sizes
from .unified_database_initializer import initialize_database

logger = logging.getLogger(__name__)

SIZE_THRESHOLD_MB = 99.9
SKIP_THRESHOLD_MB = 100.0
BACKUP_ROOT = Path(os.getenv("GH_COPILOT_BACKUP_ROOT", "/temp/gh_COPILOT_Backups"))
BACKUP_DIR = BACKUP_ROOT / "database_backups"


def archive_database(db_path: Path, dest_dir: Path, level: int = 9) -> Path:
    """Archive ``db_path`` to ``dest_dir`` using 7z with maximum compression."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    archive_path = dest_dir / f"{db_path.name}.7z"
    with py7zr.SevenZipFile(
        archive_path, "w", filters=[{"id": py7zr.FILTER_LZMA2, "preset": level}]
    ) as zf:
        zf.write(db_path, arcname=db_path.name)
    logger.info("Archived %s to %s", db_path.name, archive_path)
    return archive_path


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
    workspace: Path,
    sources: Iterable[str],
    log_file: Union[Path, str] = "migration.log",
) -> None:
    """Migrate ``sources`` into ``enterprise_assets.db`` with compression."""
    validate_enterprise_operation()
    db_dir = workspace / "databases"
    enterprise_db = db_dir / "enterprise_assets.db"
    initialize_database(enterprise_db)
    backup_dir = BACKUP_DIR

    handler = logging.FileHandler(log_file)
    logger.addHandler(handler)
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    start_ts = datetime.now()
    logger.info("Session %s started at %s", session_id, start_ts.isoformat())

    conn: Optional[sqlite3.Connection] = None
    try:
        conn = sqlite3.connect(enterprise_db)
        conn.execute("BEGIN IMMEDIATE")
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
                migrator.target_conn = conn
                migrator.migration_report = {"errors": []}
                migrator.migrate_database_content()
                analysis = migrator.analyze_database_structure(enterprise_db)
                compress_large_tables(enterprise_db, analysis)
                elapsed = perf_counter() - start
                remaining = (total - idx) * (elapsed / idx)
                bar.set_postfix(ETC=f"{remaining:.1f}s")
                bar.update(1)

        if not check_database_sizes(db_dir):
            raise RuntimeError("Database size limit exceeded")
        conn.commit()
        logger.info("Consolidation complete")
    except Exception as exc:
        logger.exception("Migration failed: %s", exc)
        if conn is not None:
            try:
                conn.rollback()
            except Exception:
                pass
        raise
    finally:
        if conn is not None:
            conn.close()
        end_ts = datetime.now()
        duration = (end_ts - start_ts).total_seconds()
        logger.info(
            "Session %s ended at %s (%.2fs)",
            session_id,
            end_ts.isoformat(),
            duration,
        )
        logger.removeHandler(handler)
        handler.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Consolidate enterprise databases")
    parser.add_argument(
        "--log-file",
        type=Path,
        default=Path("migration.log"),
        help="Path to the migration log file",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    migrate_and_compress(
        workspace,
        ["analytics.db", "documentation.db", "template_completion.db"],
        log_file=args.log_file,
    )
