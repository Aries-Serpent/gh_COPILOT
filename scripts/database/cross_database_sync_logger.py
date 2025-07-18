#!/usr/bin/env python3
"""Log cross-database sync operations."""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .unified_database_initializer import initialize_database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    """Return True if ``table`` exists in the database."""
    result = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    ).fetchone()
    return result is not None


def log_sync_operation(db_path: Path, operation: str) -> None:
    """Insert a sync operation record into the tracking table."""
    if not db_path.exists():
        initialize_database(db_path)

    timestamp = datetime.now(timezone.utc).isoformat()
    conn = sqlite3.connect(db_path)
    try:
        if not _table_exists(conn, "cross_database_sync_operations"):
            conn.close()
            initialize_database(db_path)
            conn = sqlite3.connect(db_path)
        conn.execute(
            "INSERT INTO cross_database_sync_operations (operation, timestamp)"
            " VALUES (?, ?)",
            (operation, timestamp),
        )
        conn.commit()
    finally:
        conn.close()
    logger.info("Logged sync operation %s at %s", operation, timestamp)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Log a sync operation")
    parser.add_argument(
        "--database",
        default=Path(__file__).resolve().parents[1] / "databases" / "enterprise_assets.db",
        type=Path,
        help="Path to enterprise_assets.db",
    )
    parser.add_argument(
        "operation",
        default="manual_invocation",
        help="Operation description",
    )

    args = parser.parse_args()
    log_sync_operation(args.database, args.operation)
