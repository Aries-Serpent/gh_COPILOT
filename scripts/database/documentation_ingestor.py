#!/usr/bin/env python3
"""Ingest Markdown files into documentation_assets table."""

from __future__ import annotations

import hashlib
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from tqdm import tqdm

from enterprise_modules.compliance import validate_enterprise_operation
from template_engine.learning_templates import get_dataset_sources

from .cross_database_sync_logger import _table_exists, log_sync_operation
from .size_compliance_checker import check_database_sizes
from .unified_database_initializer import initialize_database

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def _gather_markdown_files(directory: Path) -> list[Path]:
    """Return a sorted list of Markdown files under ``directory``."""
    files = [p for p in directory.rglob("*.md") if p.is_file()]
    return sorted(files)


def ingest_documentation(
    workspace: Path,
    docs_dir: Path | None = None,
    timeout_seconds: int | None = None,
) -> None:
    """Ingest Markdown files into ``enterprise_assets.db``.

    Parameters
    ----------
    workspace:
        The workspace root containing the ``databases`` directory.
    docs_dir:
        Optional path to the documentation directory. Defaults to
        ``workspace / 'documentation'``.
    """
    validate_enterprise_operation()

    db_dir = workspace / "databases"
    db_path = db_dir / "enterprise_assets.db"

    if not db_path.exists():
        initialize_database(db_path)

    docs_dir = docs_dir or (workspace / "documentation")
    files = _gather_markdown_files(docs_dir)

    dataset_dbs = get_dataset_sources(str(workspace))
    existing_docs: set[str] = set()
    existing_hashes: set[str] = set()

    if db_path.exists():
        try:
            with sqlite3.connect(db_path) as conn:
                if _table_exists(conn, "documentation_assets"):
                    existing_docs.update(
                        row[0]
                        for row in conn.execute(
                            "SELECT doc_path FROM documentation_assets"
                        )
                    )
                    existing_hashes.update(
                        row[0]
                        for row in conn.execute(
                            "SELECT content_hash FROM documentation_assets"
                        )
                    )
        except sqlite3.Error:
            existing_docs = set()
            existing_hashes = set()

    primary_db = dataset_dbs[0] if dataset_dbs else None
    if primary_db and primary_db.exists() and primary_db != db_path:
        try:
            with sqlite3.connect(primary_db) as prod_conn:
                if _table_exists(prod_conn, "documentation_assets"):
                    existing_docs.update(
                        row[0]
                        for row in prod_conn.execute(
                            "SELECT doc_path FROM documentation_assets"
                        )
                    )
                    existing_hashes.update(
                        row[0]
                        for row in prod_conn.execute(
                            "SELECT content_hash FROM documentation_assets"
                        )
                    )
        except sqlite3.Error:
            pass

    start_time = datetime.now(timezone.utc)
    logger.info("Starting documentation ingestion at %s", start_time.isoformat())

    conn = sqlite3.connect(db_path)
    try:
        if not _table_exists(conn, "documentation_assets"):
            conn.close()
            initialize_database(db_path)
            conn = sqlite3.connect(db_path)
        with conn, tqdm(total=len(files), desc="Docs", unit="file") as bar:
            for path in files:
                if timeout_seconds and (datetime.now(timezone.utc) - start_time).total_seconds() > timeout_seconds:
                    logger.error("Ingestion timed out")
                    raise TimeoutError("Documentation ingestion timed out")

                rel_path = str(path.relative_to(workspace))
                if path.stat().st_size == 0 or rel_path in existing_docs:
                    if path.stat().st_size == 0:
                        logger.warning("Skipping zero-byte file: %s", path)
                    bar.update(1)
                    continue

                content = path.read_text(encoding="utf-8")
                digest = hashlib.sha256(content.encode()).hexdigest()
                if digest in existing_hashes:
                    bar.update(1)
                    continue
                modified_at = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()
                conn.execute(
                    (
                        "INSERT INTO documentation_assets "
                        "(doc_path, content_hash, created_at, modified_at) "
                        "VALUES (?, ?, ?, ?)"
                    ),
                    (
                        rel_path,
                        digest,
                        datetime.now(timezone.utc).isoformat(),
                        modified_at,
                    ),
                )
                bar.update(1)
                existing_docs.add(rel_path)
                existing_hashes.add(digest)
    finally:
        conn.commit()
        conn.close()

    log_sync_operation(db_path, "documentation_ingestion", start_time=start_time)

    if not check_database_sizes(db_dir):
        raise RuntimeError("Database size limit exceeded")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ingest documentation")
    parser.add_argument(
        "--workspace",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Workspace root",
    )
    parser.add_argument(
        "--docs-dir",
        type=Path,
        help="Directory containing markdown files",
    )

    args = parser.parse_args()
    ingest_documentation(args.workspace, args.docs_dir)
