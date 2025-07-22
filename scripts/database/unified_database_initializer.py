#!/usr/bin/env python3
"""Initialize the enterprise_assets.db database."""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

# STUB TASK PROMPT: Ensure all required tables are defined in enterprise_assets.db.
# Tables: script_assets, documentation_assets, template_assets, pattern_assets,
# enterprise_metadata, integration_tracking, cross_database_sync_operations
# If any table is missing, generate CREATE TABLE statements and add to TABLES dict.
# Validate schema matches compliance requirements (column types, constraints,
# indexes).
# Add visual processing indicators (start time logging, progress bar, timeout, etc).
# Add dual copilot validation hooks.

from utils.logging_utils import setup_enterprise_logging
from utils.validation_utils import detect_zero_byte_files, validate_path
from secondary_copilot_validator import SecondaryCopilotValidator

logger = logging.getLogger(__name__)

TABLES: dict[str, str] = {
    "script_assets": (
        "CREATE TABLE IF NOT EXISTS script_assets ("
        "id INTEGER PRIMARY KEY,"
        "script_path TEXT NOT NULL,"
        "content_hash TEXT NOT NULL,"
        "created_at TEXT NOT NULL"
        ")"
    ),
    "documentation_assets": (
        "CREATE TABLE IF NOT EXISTS documentation_assets ("
        "id INTEGER PRIMARY KEY,"
        "doc_path TEXT NOT NULL,"
        "content_hash TEXT NOT NULL,"
        "created_at TEXT NOT NULL,"
        "modified_at TEXT NOT NULL"
        ")"
    ),
    "template_assets": (
        "CREATE TABLE IF NOT EXISTS template_assets ("
        "id INTEGER PRIMARY KEY,"
        "template_path TEXT NOT NULL,"
        "content_hash TEXT NOT NULL,"
        "created_at TEXT NOT NULL"
        ")"
    ),
    "pattern_assets": (
        "CREATE TABLE IF NOT EXISTS pattern_assets ("
        "id INTEGER PRIMARY KEY,"
        "pattern TEXT NOT NULL,"
        "usage_count INTEGER DEFAULT 0,"
        "created_at TEXT NOT NULL"
        ")"
    ),
    "enterprise_metadata": (
        "CREATE TABLE IF NOT EXISTS enterprise_metadata ("
        "id INTEGER PRIMARY KEY,"
        "key TEXT NOT NULL,"
        "value TEXT NOT NULL"
        ")"
    ),
    "integration_tracking": (
        "CREATE TABLE IF NOT EXISTS integration_tracking ("
        "id INTEGER PRIMARY KEY,"
        "integration_name TEXT NOT NULL,"
        "status TEXT NOT NULL,"
        "last_synced TEXT"
        ")"
    ),
    "cross_database_sync_operations": (
        "CREATE TABLE IF NOT EXISTS cross_database_sync_operations ("
        "id INTEGER PRIMARY KEY,"
        "operation TEXT NOT NULL,"
        "status TEXT NOT NULL,"
        "start_time TEXT NOT NULL,"
        "duration REAL NOT NULL,"
        "timestamp TEXT NOT NULL"
        ")"
    ),
}


def initialize_database(db_path: Path) -> None:
    """Create enterprise_assets.db with the expected schema."""
    if not validate_path(db_path):
        raise RuntimeError(f"Invalid database path: {db_path}")
    if db_path.exists() and db_path.stat().st_size > 99_900_000:
        raise RuntimeError("Database file exceeds 99.9 MB")
    zeros = detect_zero_byte_files(db_path.parent)
    if zeros:
        raise RuntimeError(f"Zero-byte files detected: {zeros}")

    logger.info("Initializing %s", db_path)
    start_time = datetime.now()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path, timeout=5) as conn, tqdm(
        total=len(TABLES), desc="Creating tables", unit="table"
    ) as bar:
        for sql in TABLES.values():
            conn.execute(sql)
            bar.update(1)
        conn.commit()
    duration = (datetime.now() - start_time).total_seconds()
    logger.info("Database initialization complete in %.2fs", duration)

    SecondaryCopilotValidator(logger).validate_corrections([__file__])


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    db_path = root / "databases" / "enterprise_assets.db"
    if db_path.exists():
        logger.info("%s already exists", db_path)
        return
    initialize_database(db_path)


if __name__ == "__main__":
    setup_enterprise_logging()
    main()
