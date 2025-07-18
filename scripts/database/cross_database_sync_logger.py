#!/usr/bin/env python3
"""Log cross-database sync operations."""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from tqdm import tqdm

from utils.logging_utils import setup_enterprise_logging

from .unified_database_initializer import initialize_database

logger = logging.getLogger(__name__)

# Text-based indicators for consistent log output
TEXT_INDICATORS = {
    "start": "[START]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
    "progress": "[PROGRESS]",
}


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    """Return True if ``table`` exists in the database."""
    result = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    ).fetchone()
    return result is not None


def log_sync_operation(db_path: Path, operation: str) -> None:
    """Insert a sync operation record into the tracking table with progress."""

    start_dt = datetime.now(timezone.utc)
    logger.info(
        "%s Logging sync operation %s at %s",
        TEXT_INDICATORS["start"],
        operation,
        start_dt.isoformat(),
    )

    with tqdm(
        total=3,
        desc=f"{TEXT_INDICATORS['progress']} log_sync",
        unit="step",
        bar_format="{l_bar}{bar}| {n}/{total} {unit} [{elapsed}<{remaining}]",
    ) as bar:
        if not db_path.exists():
            initialize_database(db_path)
        bar.update(1)

        timestamp = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(db_path) as conn:
            if not _table_exists(conn, "cross_database_sync_operations"):
                conn.close()
                initialize_database(db_path)
                conn = sqlite3.connect(db_path)
            bar.update(1)
            with conn:
                conn.execute(
                    "INSERT INTO cross_database_sync_operations (operation, timestamp)"
                    " VALUES (?, ?)",
                    (operation, timestamp),
                )
                conn.commit()
            bar.update(1)

    duration = (datetime.now(timezone.utc) - start_dt).total_seconds()
    logger.info(
        "%s Logged sync operation %s in %.2fs",
        TEXT_INDICATORS["success"],
        operation,
        duration,
    )


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
    setup_enterprise_logging()
    log_sync_operation(args.database, args.operation)
