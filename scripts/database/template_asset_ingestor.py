#!/usr/bin/env python3
"""Ingest templates and patterns into enterprise_assets.db."""

from __future__ import annotations

import hashlib
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from tqdm import tqdm

from enterprise_modules.compliance import validate_enterprise_operation
from template_engine.learning_templates import get_dataset_sources, get_lesson_templates
from .cross_database_sync_logger import _table_exists, log_sync_operation
from .size_compliance_checker import check_database_sizes
from .unified_database_initializer import initialize_database

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def _gather_template_files(directory: Path) -> list[Path]:
    """Return a sorted list of Markdown template files under ``directory``."""
    files = [p for p in directory.rglob("*.md") if p.is_file()]
    return sorted(files)


def ingest_templates(workspace: Path, template_dir: Path | None = None) -> None:
    """Load template and pattern data into ``enterprise_assets.db``.

    Parameters
    ----------
    workspace:
        The workspace root containing the ``databases`` directory.
    template_dir:
        Optional path to the template directory. Defaults to
        ``workspace / 'prompts'``.
    """
    validate_enterprise_operation()

    db_dir = workspace / "databases"
    db_path = db_dir / "enterprise_assets.db"

    if not db_path.exists():
        initialize_database(db_path)

    template_dir = template_dir or (workspace / "prompts")
    files = _gather_template_files(template_dir)

    dataset_dbs = get_dataset_sources(str(workspace))
    existing_paths: set[str] = set()
    existing_hashes: set[str] = set()

    if db_path.exists():
        try:
            with sqlite3.connect(db_path) as conn:
                if _table_exists(conn, "template_assets"):
                    existing_paths.update(
                        row[0]
                        for row in conn.execute(
                            "SELECT template_path FROM template_assets"
                        )
                    )
                    existing_hashes.update(
                        row[0]
                        for row in conn.execute(
                            "SELECT content_hash FROM template_assets"
                        )
                    )
        except sqlite3.Error:
            existing_paths = set()
            existing_hashes = set()

    primary_db = dataset_dbs[0] if dataset_dbs else None
    if primary_db and primary_db.exists() and primary_db != db_path:
        try:
            with sqlite3.connect(primary_db) as prod_conn:
                if _table_exists(prod_conn, "template_assets"):
                    existing_paths.update(
                        row[0]
                        for row in prod_conn.execute(
                            "SELECT template_path FROM template_assets"
                        )
                    )
                    existing_hashes.update(
                        row[0]
                        for row in prod_conn.execute(
                            "SELECT content_hash FROM template_assets"
                        )
                    )
        except sqlite3.Error:
            pass

    start_time = datetime.now(timezone.utc)

    conn = sqlite3.connect(db_path)
    try:
        if not _table_exists(conn, "template_assets"):
            conn.close()
            initialize_database(db_path)
            conn = sqlite3.connect(db_path)
        with conn, tqdm(total=len(files), desc="Templates", unit="file") as bar:
            for path in files:
                rel_path = str(path.relative_to(workspace))
                content = path.read_text(encoding="utf-8")
                digest = hashlib.sha256(content.encode()).hexdigest()
                if rel_path in existing_paths or digest in existing_hashes:
                    bar.update(1)
                    continue
                conn.execute(
                    (
                        "INSERT INTO template_assets (template_path, content_hash, created_at) VALUES (?, ?, ?)"
                    ),
                    (
                        rel_path,
                        digest,
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                conn.execute(
                    ("INSERT INTO pattern_assets (pattern, usage_count, created_at) VALUES (?, 0, ?)"),
                    (content[:1000], datetime.now(timezone.utc).isoformat()),
                )
                bar.update(1)
                existing_paths.add(rel_path)
                existing_hashes.add(digest)
        lesson_templates = get_lesson_templates()
        existing_lessons = {
            row[0]
            for row in conn.execute(
                "SELECT lesson_name FROM pattern_assets WHERE lesson_name IS NOT NULL"
            )
        }
        for name, content in lesson_templates.items():
            if name in existing_lessons:
                continue
            conn.execute(
                (
                    "INSERT INTO pattern_assets (pattern, usage_count, lesson_name, created_at) VALUES (?, 0, ?, ?)"
                ),
                (
                    content[:1000],
                    name,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
    finally:
        conn.commit()
        conn.close()

    log_sync_operation(db_path, "template_ingestion", start_time=start_time)

    if not check_database_sizes(db_dir):
        raise RuntimeError("Database size limit exceeded")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ingest templates")
    parser.add_argument(
        "--workspace",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Workspace root",
    )
    parser.add_argument(
        "--templates-dir",
        type=Path,
        help="Directory containing template markdown files",
    )

    args = parser.parse_args()
    ingest_templates(args.workspace, args.templates_dir)
