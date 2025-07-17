#!/usr/bin/env python3
"""Log cross-database sync operations."""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def log_sync_operation(db_path: Path, operation: str) -> None:
    """Insert a sync operation record into the tracking table."""
    timestamp = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO cross_database_sync_operations (operation, timestamp)"
            " VALUES (?, ?)",
            (operation, timestamp),
        )
        conn.commit()
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
    if not args.database.exists():
        logger.error("Database not found: %s", args.database)
    else:
        log_sync_operation(args.database, args.operation)
