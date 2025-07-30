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

    start_time = datetime.now(timezone.utc)

    conn = sqlite3.connect(db_path)
    try:
        if not _table_exists(conn, "template_assets"):
            conn.close()
            initialize_database(db_path)
            conn = sqlite3.connect(db_path)
        with conn, tqdm(total=len(files), desc="Templates", unit="file") as bar:
            for path in files:
                content = path.read_text(encoding="utf-8")
                digest = hashlib.sha256(content.encode()).hexdigest()
                conn.execute(
                    (
                        "INSERT INTO template_assets (template_path, content_hash, created_at)"
                        " VALUES (?, ?, ?)"
                    ),
                    (
                        str(path.relative_to(workspace)),
                        digest,
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                conn.execute(
                    (
                        "INSERT INTO pattern_assets (pattern, usage_count, created_at)"
                        " VALUES (?, 0, ?)"
                    ),
                    (content[:1000], datetime.now(timezone.utc).isoformat()),
                )
                bar.update(1)
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
