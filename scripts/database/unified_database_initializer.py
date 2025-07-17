#!/usr/bin/env python3
"""Initialize the enterprise_assets.db database."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
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
        "created_at TEXT NOT NULL"
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
        "timestamp TEXT NOT NULL"
        ")"
    ),
}


def initialize_database(db_path: Path) -> None:
    """Create enterprise_assets.db with the expected schema."""
    logger.info("Initializing %s", db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn, tqdm(
        total=len(TABLES), desc="Creating tables", unit="table"
    ) as bar:
        for sql in TABLES.values():
            conn.execute(sql)
            bar.update(1)
        conn.commit()
    logger.info("Database initialization complete")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    db_path = root / "databases" / "enterprise_assets.db"
    if db_path.exists():
        logger.info("%s already exists", db_path)
        return
    initialize_database(db_path)


if __name__ == "__main__":
    main()
