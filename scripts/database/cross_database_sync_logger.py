#!/usr/bin/env python3
"""Log cross-database sync operations."""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def log_sync_operation(db_path: Path, operation: str) -> None:
    """Insert a sync operation record into the tracking table."""
    timestamp = datetime.utcnow().isoformat()
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO cross_database_sync_operations (operation, timestamp)"
            " VALUES (?, ?)",
            (operation, timestamp),
        )
        conn.commit()
    logger.info("Logged sync operation %s at %s", operation, timestamp)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    db_path = root / "databases" / "enterprise_assets.db"
    if not db_path.exists():
        logger.error("Database not found: %s", db_path)
    else:
        log_sync_operation(db_path, "manual invocation")
