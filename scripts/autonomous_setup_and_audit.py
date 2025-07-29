"""Enterprise automation script skeleton for setup and auditing."""

from __future__ import annotations

import logging
import os
import sqlite3
from pathlib import Path
from typing import Optional

from tqdm import tqdm

from secondary_copilot_validator import SecondaryCopilotValidator

from scripts.code_placeholder_audit import main as placeholder_audit


LOGGER = logging.getLogger(__name__)


def init_database(db_path: Path) -> None:
    """Create database if it does not exist."""
    if not db_path.exists():
        conn = sqlite3.connect(db_path)
        conn.close()
        LOGGER.info("Created database %s", db_path)


def ingest_assets(doc_path: Path, template_path: Path, db_path: Path) -> None:
    """Load markdown documentation and template assets into ``db_path``.

    This replicates the behavior of :mod:`documentation_ingestor` and
    :mod:`template_asset_ingestor` but targets ``production.db`` instead of
    ``enterprise_assets.db``.
    """
    LOGGER.info("Ingesting assets from %s and %s", doc_path, template_path)

    import hashlib
    from datetime import datetime, timezone

    from scripts.database.cross_database_sync_logger import log_sync_operation

    # Gather files
    doc_files = [p for p in doc_path.rglob("*.md") if p.is_file()] if doc_path.exists() else []
    tmpl_files = [p for p in template_path.rglob("*.md") if p.is_file()] if template_path.exists() else []

    conn = sqlite3.connect(db_path)
    try:
        # Ensure required tables exist
        conn.execute(
            "CREATE TABLE IF NOT EXISTS documentation_assets ("
            "id INTEGER PRIMARY KEY,"
            "doc_path TEXT NOT NULL,"
            "content_hash TEXT NOT NULL,"
            "created_at TEXT NOT NULL,"
            "modified_at TEXT NOT NULL"
            ")"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS template_assets ("
            "id INTEGER PRIMARY KEY,"
            "template_path TEXT NOT NULL,"
            "content_hash TEXT NOT NULL,"
            "created_at TEXT NOT NULL"
            ")"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS pattern_assets ("
            "id INTEGER PRIMARY KEY,"
            "pattern TEXT NOT NULL,"
            "usage_count INTEGER DEFAULT 0,"
            "created_at TEXT NOT NULL"
            ")"
        )

        start_docs = datetime.now(timezone.utc)
        with tqdm(total=len(doc_files), desc="Docs", unit="file") as bar:
            for path in doc_files:
                if path.stat().st_size == 0:
                    bar.update(1)
                    continue
                content = path.read_text(encoding="utf-8")
                digest = hashlib.sha256(content.encode()).hexdigest()
                modified_at = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()
                conn.execute(
                    "INSERT INTO documentation_assets (doc_path, content_hash, created_at, modified_at)"
                    " VALUES (?, ?, ?, ?)",
                    (
                        str(path.relative_to(doc_path.parent)),
                        digest,
                        datetime.now(timezone.utc).isoformat(),
                        modified_at,
                    ),
                )
                bar.update(1)
        conn.commit()
        log_sync_operation(db_path, "documentation_ingestion", start_time=start_docs)

        start_tmpl = datetime.now(timezone.utc)
        with tqdm(total=len(tmpl_files), desc="Templates", unit="file") as bar:
            for path in tmpl_files:
                content = path.read_text(encoding="utf-8")
                digest = hashlib.sha256(content.encode()).hexdigest()
                conn.execute(
                    "INSERT INTO template_assets (template_path, content_hash, created_at) VALUES (?, ?, ?)",
                    (
                        str(path.relative_to(template_path.parent)),
                        digest,
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                conn.execute(
                    "INSERT INTO pattern_assets (pattern, usage_count, created_at) VALUES (?, 0, ?)",
                    (content[:1000], datetime.now(timezone.utc).isoformat()),
                )
                bar.update(1)
        conn.commit()
        log_sync_operation(db_path, "template_ingestion", start_time=start_tmpl)
    finally:
        conn.close()


def run_audit(workspace: Path, analytics_db: Path, production_db: Optional[Path], dashboard_dir: Path) -> None:
    """Run placeholder audit with visual progress."""
    LOGGER.info("Starting placeholder audit")
    placeholder_audit(
        workspace_path=str(workspace),
        analytics_db=str(analytics_db),
        production_db=str(production_db) if production_db else None,
        dashboard_dir=str(dashboard_dir),
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", "."))
    analytics_db = workspace / "databases" / "analytics.db"
    production_db = workspace / "databases" / "production.db"
    dashboard_dir = workspace / "dashboard" / "compliance"

    init_database(analytics_db)
    init_database(production_db)

    ingest_assets(workspace / "documentation", workspace / "template_engine", production_db)

    run_audit(workspace, analytics_db, production_db, dashboard_dir)

    validator = SecondaryCopilotValidator()
    validator.validate_corrections([__file__])

    LOGGER.info("Automation complete")


if __name__ == "__main__":
    main()
