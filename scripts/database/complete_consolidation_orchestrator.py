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
from typing import Iterable, List, Optional

import py7zr
from tqdm import tqdm

from scripts.continuous_operation_orchestrator import \
    validate_enterprise_operation

from .database_migration_corrector import DatabaseMigrationCorrector
from .size_compliance_checker import check_database_sizes
from .unified_database_initializer import initialize_database

logger = logging.getLogger(__name__)


def export_table_to_7z(db_path: Path, table: str, dest_dir: Path) -> Path:
    """Export ``table`` from ``db_path`` to ``dest_dir`` as a 7z archive."""
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
    with py7zr.SevenZipFile(archive_path, "w") as zf:
        zf.write(tmp_path, arcname=tmp_path.name)
    tmp_path.unlink()
    logger.info("Compressed %s.%s to %s", db_path.name, table, archive_path)
    return archive_path


def compress_large_tables(db_path: Path, analysis: dict, threshold: int = 50000) -> List[Path]:
    """Compress tables with a row count greater than ``threshold``."""
    archives: List[Path] = []
    for table in analysis.get("tables", []):
        if table.get("record_count", 0) > threshold:
            archives.append(export_table_to_7z(
                db_path, table["name"], Path("archives/table_exports")))
    return archives


def migrate_and_compress(
    workspace: Path,
    sources: Iterable[str],
    log_file: Path | str = "migration.log",
) -> None:
    """Migrate ``sources`` into ``enterprise_assets.db`` with compression."""
    validate_enterprise_operation()
    db_dir = workspace / "databases"
    enterprise_db = db_dir / "enterprise_assets.db"
    initialize_database(enterprise_db)

    handler = logging.FileHandler(log_file)
    logger.addHandler(handler)
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    start_ts = datetime.now()
    logger.info("Session %s started at %s", session_id, start_ts.isoformat())

    conn: Optional[sqlite3.Connection] = None
    try:
        conn = sqlite3.connect(enterprise_db)
        conn.execute("BEGIN")
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
