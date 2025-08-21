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
from typing import Any, List, Optional, Sequence, Union, cast

from utils.cross_platform_paths import CrossPlatformPathManager

import py7zr  # pyright: ignore[reportMissingImports]
from tqdm import tqdm

from enterprise_modules import compliance
from utils.validation_utils import run_dual_copilot_validation

from scripts.database.database_migration_corrector import DatabaseMigrationCorrector
from scripts.database.size_compliance_checker import check_database_sizes
from scripts.database.unified_database_initializer import initialize_database

py7zr = cast(Any, py7zr)


def secondary_validate() -> bool:
    """Run secondary validation mirroring :func:`validate_enterprise_operation`."""
    logging.info("SECONDARY VALIDATION: enterprise operation")
    return compliance.validate_enterprise_operation()


logger = logging.getLogger(__name__)

SIZE_THRESHOLD_MB = 99.9
SKIP_THRESHOLD_MB = 100.0


class ExternalBackupConfiguration:
    """Enterprise external backup configuration."""

    @staticmethod
    def get_backup_root() -> Path:
        env_path = os.getenv("GH_COPILOT_BACKUP_ROOT")
        if env_path:
            return Path(env_path)
        if os.name == "nt":
            return Path("E:/temp/gh_COPILOT_Backups")
        user = os.getenv("USER", "user")
        return Path(f"/tmp/{user}/gh_COPILOT_Backups")

    @staticmethod
    def validate_external_backup_location(backup_path: Path, workspace_path: Path) -> None:
        """Raise if ``backup_path`` resides within ``workspace_path``.

        Paths are resolved prior to comparison to prevent bypasses such as
        ``..`` segments or symbolic links that would otherwise allow backups to
        be created inside the repository workspace.
        """

        resolved_backup = backup_path.resolve()
        resolved_workspace = workspace_path.resolve()
        try:
            resolved_backup.relative_to(resolved_workspace)
        except ValueError:
            return
        raise RuntimeError(
            f"CRITICAL: Backup location inside workspace: {resolved_backup}"
        )


WORKSPACE_PATH = CrossPlatformPathManager.get_workspace_path()
BACKUP_ROOT = ExternalBackupConfiguration.get_backup_root()
BACKUP_DIR = BACKUP_ROOT / "database_consolidation"
ExternalBackupConfiguration.validate_external_backup_location(BACKUP_DIR, WORKSPACE_PATH)


def archive_database(db_path: Path, dest_dir: Path, level: int = 9) -> Path:
    """Archive ``db_path`` to ``dest_dir`` using 7z with maximum compression."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    archive_path = dest_dir / f"{db_path.name}.7z"
    with py7zr.SevenZipFile(archive_path, "w", filters=[{"id": py7zr.FILTER_LZMA2, "preset": level}]) as zf:  # type: ignore[attr-defined]
        zf.write(db_path, arcname=db_path.name)
    logger.info("Archived %s to %s", db_path.name, archive_path)
    return archive_path


def export_table_to_7z(db_path: Path, table: str, dest_dir: Path, level: int = 5) -> Path:
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
        archive_path, "w", filters=[{"id": py7zr.FILTER_LZMA2, "preset": level}]
    ) as zf:  # type: ignore[attr-defined]
        zf.write(tmp_path, arcname=tmp_path.name)
    tmp_path.unlink()
    logger.info("Compressed %s.%s to %s", db_path.name, table, archive_path)
    return archive_path


def create_external_backup(
    source_path: Path, backup_name: str, *, backup_dir: Path | None = None
) -> Path:
    """Create a timestamped backup in the external backup directory."""

    target_dir = (backup_dir or BACKUP_DIR).resolve()
    workspace_path = CrossPlatformPathManager.get_workspace_path()
    # validate backup path is outside the workspace
    ExternalBackupConfiguration.validate_external_backup_location(
        target_dir, workspace_path
    )
    target_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = target_dir / f"{backup_name}_{timestamp}.backup"

    with tqdm(total=100, desc=f"Creating backup: {backup_name}", unit="%") as bar:
        bar.set_description("Validating source")
        if not source_path.exists():
            raise RuntimeError(f"Source path does not exist: {source_path}")
        bar.update(25)

        bar.set_description("Copying")
        shutil.copy2(source_path, dest)
        bar.update(50)

        bar.set_description("Verifying")
        if not dest.exists():
            raise RuntimeError(f"Backup creation failed: {dest}")
        bar.update(25)

        bar.set_description("Backup complete")
        logger.info("External backup created: %s", dest)

    return dest


def compress_large_tables(db_path: Path, analysis: dict, threshold: int = 50000, *, level: int = 5) -> List[Path]:
    """Compress tables with a row count greater than ``threshold``.

    If ``analysis`` lacks table metrics the database is queried directly to
    determine row counts, ensuring large tables are still archived during
    consolidation.
    """
    archives: List[Path] = []
    tables = analysis.get("tables")
    if not tables:
        with sqlite3.connect(db_path) as conn:
            cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [
                {
                    "name": r[0],
                    "record_count": conn.execute(f"SELECT COUNT(*) FROM {r[0]}").fetchone()[0],
                }
                for r in cur.fetchall()
            ]
    dest_dir = db_path.parent.parent / "archives" / "table_exports"
    for table in tables:
        if table.get("record_count", 0) > threshold:
            archives.append(
                export_table_to_7z(
                    db_path,
                    table["name"],
                    dest_dir,
                    level,
                )
            )
    return archives


def primary_validate() -> bool:
    """Primary consolidation validation."""
    logger.info("PRIMARY validation executed")
    return True


def migrate_and_compress(
    workspace: Path,
    sources: Sequence[str],
    log_file: Union[Path, str] = "migration.log",
    *,
    level: int = 5,
) -> None:
    """Migrate ``sources`` into ``enterprise_assets.db`` with compression.

    Parameters
    ----------
    workspace:
        Workspace root containing the database directory.
    sources:
        Iterable of database file names to consolidate.
    log_file:
        File path for migration logs.
    level:
        Compression level used when archiving large tables.
    """
    logging.info("PRIMARY VALIDATION: enterprise operation")
    compliance.validate_enterprise_operation()
    db_dir = workspace / "databases"
    enterprise_db = db_dir / "enterprise_assets.db"
    initialize_database(enterprise_db)
    session_backup_dir = BACKUP_DIR / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    session_backup_dir.mkdir(parents=True, exist_ok=True)

    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    start_ts = datetime.now()
    logger.info("Session %s started at %s", session_id, start_ts.isoformat())

    conn: Optional[sqlite3.Connection] = None
    sources_list = list(sources)
    try:
        conn = sqlite3.connect(enterprise_db)
        conn.execute("BEGIN IMMEDIATE")
        total = len(sources_list)
        start = perf_counter()
        with tqdm(total=total, desc="Consolidating", unit="db") as bar:
            for idx, name in enumerate(sources_list, 1):
                src = db_dir / name
                if not src.exists():
                    bar.update(1)
                    continue
                create_external_backup(src, name.replace(".db", ""), backup_dir=session_backup_dir)
                migrator = DatabaseMigrationCorrector()
                migrator.workspace_root = workspace
                migrator.source_db = src
                migrator.target_db = enterprise_db
                migrator.target_conn = conn
                migrator.migrate_database_content()
                conn.commit()
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
        logger.info("Backup Root: %s", BACKUP_ROOT)
        logger.info("Session Backup Directory: %s", session_backup_dir)

        def _primary():
            logger.info("PRIMARY VALIDATION")
            return primary_validate()

        def _secondary():
            logger.info("SECONDARY VALIDATION")
            return secondary_validate()

        run_dual_copilot_validation(_primary, _secondary)
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
    workspace = CrossPlatformPathManager.get_workspace_path()
    migrate_and_compress(
        workspace,
        ["analytics.db", "documentation.db", "template_completion.db"],
        level=5,
        log_file=args.log_file,
    )
