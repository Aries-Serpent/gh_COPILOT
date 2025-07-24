#!/usr/bin/env python3
"""Cross-database sync operation logger.

This module provides :func:`log_sync_operation` which records an operation name,
status, caller supplied start time, calculated duration and a timestamp to the
``cross_database_sync_operations`` table.  The
``validate_enterprise_operation`` guard is executed before any write occurs and
CLI usage displays a progress bar when logging multiple operations.
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from scripts.continuous_operation_orchestrator import validate_enterprise_operation
from utils.logging_utils import setup_enterprise_logging

logger = logging.getLogger(__name__)


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    """Return True if ``table`` exists in the database."""
    result = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    ).fetchone()
    return result is not None


def log_sync_operation(
    db_path: Path,
    operation: str,
    *,
    status: str = "SUCCESS",
    start_time: datetime | None = None,
) -> datetime:
    """Insert a sync operation record and return the start timestamp.

    ``start_time`` should be the timestamp captured when the operation began.
    If ``None`` it is set to the current time so callers can reuse the returned
    value when logging completion events.  ``duration`` is computed from the
    captured start time to the log call time.
    """
    validate_enterprise_operation()

    if not db_path.exists():
        from .unified_database_initializer import initialize_database
        initialize_database(db_path)

    start_dt = start_time or datetime.now(timezone.utc)
    end_dt = datetime.now(timezone.utc)
    duration = (end_dt - start_dt).total_seconds()
    timestamp = end_dt.isoformat()

    with sqlite3.connect(db_path) as conn:
        if not _table_exists(conn, "cross_database_sync_operations"):
            conn.close()
            from .unified_database_initializer import initialize_database
            initialize_database(db_path)
            conn = sqlite3.connect(db_path)
        with conn:
            conn.execute(
                "INSERT INTO cross_database_sync_operations (operation, status, start_time, duration, timestamp)"
                " VALUES (?, ?, ?, ?, ?)",
                (operation, status, start_dt.isoformat(), duration, timestamp),
            )
            conn.commit()
    logger.info(
        "Logged sync operation %s at %s with status %s",
        operation,
        timestamp,
        status,
    )
    return start_dt


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
        "--status",
        default="SUCCESS",
        help="Operation status",
    )
    parser.add_argument(
        "--start-time",
        default=None,
        help="Optional start time in ISO format",
    )
    parser.add_argument(
        "operation",
        nargs="+",
        default=["manual_invocation"],
        help="Operation description(s)",
    )

    args = parser.parse_args()
    setup_enterprise_logging()

    start_dt = (
        datetime.fromisoformat(args.start_time)
        if args.start_time
        else datetime.now(timezone.utc)
    )
    ops = args.operation
    if len(ops) > 1:
        from tqdm import tqdm

        for op in tqdm(ops, desc="Logging operations"):
            log_sync_operation(args.database, op, status=args.status, start_time=start_dt)
    else:
        log_sync_operation(args.database, ops[0], status=args.status, start_time=start_dt)
