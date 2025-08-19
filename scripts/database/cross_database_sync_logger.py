#!/usr/bin/env python3
"""Cross-database sync operation logger.

This module provides :func:`log_sync_operation` which records an operation name,
status, caller supplied start time, calculated duration and a timestamp to the
``cross_database_sync_operations`` table in one or more databases.  In addition,
each call emits an analytics event via :func:`utils.log_utils.log_event` so that
sync activity is captured by the unified logging pipeline.  The
``validate_enterprise_operation`` guard is executed before any write occurs and
CLI usage displays a progress bar when logging multiple operations.
"""

from __future__ import annotations

import logging
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from enterprise_modules.compliance import validate_enterprise_operation
from utils.cross_platform_paths import CrossPlatformPathManager
from utils.log_utils import log_event
from utils.logging_utils import setup_enterprise_logging
from utils.analytics_events import log_analytics_event

logger = logging.getLogger(__name__)


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    """Return True if ``table`` exists in the database."""
    result = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    ).fetchone()
    return result is not None


def log_sync_operation(
    db_paths: Path | Iterable[Path],
    operation: str,
    *,
    status: str = "SUCCESS",
    start_time: datetime | None = None,
) -> datetime:
    """Insert a sync operation record and return the start timestamp.

    ``db_paths`` may be a single path or an iterable of paths.  The operation
    entry is written to each database in a best-effort atomic transaction.  If
    any insert fails, all previous inserts are rolled back.

    ``start_time`` should be the timestamp captured when the operation began.
    If ``None`` it is set to the current time so callers can reuse the returned
    value when logging completion events.  ``duration`` is computed from the
    captured start time to the log call time.
    """
    validate_enterprise_operation()

    paths: list[Path] = [db_paths] if isinstance(db_paths, Path) else [Path(p) for p in db_paths]

    if start_time is not None and start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)
    start_dt = start_time or datetime.now(timezone.utc)
    end_dt = datetime.now(timezone.utc)
    duration = (end_dt - start_dt).total_seconds()
    timestamp = end_dt.isoformat()

    connections: list[sqlite3.Connection] = []
    try:
        for db_path in paths:
            if not db_path.exists():
                from .unified_database_initializer import initialize_database

                initialize_database(db_path)

            conn = sqlite3.connect(db_path)
            if not _table_exists(conn, "cross_database_sync_operations"):
                conn.close()
                from .unified_database_initializer import initialize_database

                initialize_database(db_path)
                conn = sqlite3.connect(db_path)
            connections.append(conn)

        for conn in connections:
            conn.execute(
                "INSERT INTO cross_database_sync_operations (operation, status, start_time, duration, timestamp)"
                " VALUES (?, ?, ?, ?, ?)",
                (operation, status, start_dt.isoformat(), duration, timestamp),
            )

        for conn in connections:
            conn.commit()
    except Exception:
        for conn in connections:
            conn.rollback()
        raise
    finally:
        for conn in connections:
            conn.close()

    logger.info(
        "Logged sync operation %s at %s with status %s",
        operation,
        timestamp,
        status,
    )
    try:
        analytics_db = Path(os.getenv("ANALYTICS_DB", "databases/analytics.db"))
        log_event(
            {
                "module": "cross_database_sync_logger",
                "level": "INFO",
                "description": operation,
                "status": status,
                "duration": duration,
                "timestamp": timestamp,
            },
            db_path=analytics_db,
        )
        log_analytics_event(
            operation,
            "sync_step",
            {"status": status, "duration": duration},
            timestamp,
        )
    except Exception as exc:  # pragma: no cover - best effort analytics logging
        logger.error("Failed to log analytics event: %s", exc)
    return start_dt


def log_sync_operation_with_analytics(
    db_paths: Path | Iterable[Path],
    operation: str,
    *,
    status: str = "SUCCESS",
    start_time: datetime | None = None,
    analytics_db: Path | None = None,
) -> datetime:
    """Log a sync operation and record an analytics event.

    This helper combines :func:`log_sync_operation` with :func:`log_event` to
    provide an audit-grade trail of synchronization activity.  ``analytics_db``
    defaults to ``databases/analytics.db`` under the current workspace.
    """

    start_dt = log_sync_operation(db_paths, operation, status=status, start_time=start_time)
    event = {
        "source": operation,
        "target": status,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    db_path = analytics_db or (CrossPlatformPathManager.get_workspace_path() / "databases" / "analytics.db")
    log_event(event, table="sync_events_log", db_path=db_path)
    return start_dt


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Log a sync operation")
    parser.add_argument(
        "--database",
        default=[Path(__file__).resolve().parents[1] / "databases" / "enterprise_assets.db"],
        type=Path,
        nargs="+",
        help="Path(s) to enterprise_assets.db",
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

    start_dt = datetime.fromisoformat(args.start_time) if args.start_time else datetime.now(timezone.utc)
    ops = args.operation
    if len(ops) > 1:
        from tqdm import tqdm

        for op in tqdm(ops, desc="Logging operations"):
            log_sync_operation(args.database, op, status=args.status, start_time=start_dt)
    else:
        log_sync_operation(args.database, ops[0], status=args.status, start_time=start_dt)


# CODEx: log_analytics_event integration hint
try:
    from tools.apply_analytics_event_workflow import log_analytics_event  # lazy import for optional use
except Exception:
    log_analytics_event = None
# Example (wrap at success/failure boundaries):
# if log_analytics_event:
#     log_analytics_event(run_id, 'sync', {'status': 'ok', 'file': __file__})
