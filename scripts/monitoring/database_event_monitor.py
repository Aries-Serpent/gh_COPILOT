#!/usr/bin/env python3
"""Database event rate monitoring utilities.

This module records row counts from the ``cross_database_sync_operations``
table for a set of databases and persists aggregated metrics to
``analytics.db``.  Sudden spikes in event rate trigger warning logs to help
operators investigate potential issues.
"""

from __future__ import annotations

import logging
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

from enterprise_modules.compliance import validate_enterprise_operation
from utils.logging_utils import log_enterprise_operation, setup_enterprise_logging
from unified_monitoring_optimization_system import _update_dashboard


logger = logging.getLogger(__name__)


def _ensure_metrics_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS event_rate_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            db_path TEXT NOT NULL,
            event_count INTEGER NOT NULL
        )
        """
    )


def _record_metrics(analytics_db: Path, db_path: Path, count: int) -> None:
    with sqlite3.connect(analytics_db) as conn:
        _ensure_metrics_table(conn)
        conn.execute(
            "INSERT INTO event_rate_metrics (timestamp, db_path, event_count) VALUES (?, ?, ?)",
            (datetime.now(timezone.utc).isoformat(), str(db_path), count),
        )
        conn.commit()


def collect_metrics(
    db_paths: Sequence[Path], analytics_db: Path, *, threshold: int = 100
) -> None:
    """Collect metrics for ``db_paths`` and store them in ``analytics_db``.

    A warning is logged if a database's row count exceeds ``threshold`` since
    the previous measurement.
    """
    validate_enterprise_operation()

    last_counts = {}
    for db_path in db_paths:
        with sqlite3.connect(db_path) as conn:
            try:
                count = conn.execute(
                    "SELECT COUNT(*) FROM cross_database_sync_operations"
                ).fetchone()[0]
            except sqlite3.OperationalError:
                log_enterprise_operation(
                    "schema_mismatch", "WARNING", f"missing cross_database_sync_operations in {db_path}"
                )
                continue

        _record_metrics(analytics_db, db_path, count)
        _update_dashboard({"db_path": str(db_path), "event_count": count})

        previous = last_counts.get(db_path)
        if previous is not None and count - previous > threshold:
            log_enterprise_operation(
                "anomalous_event_rate",
                "WARNING",
                f"count jumped from {previous} to {count} for {db_path}",
            )
        last_counts[db_path] = count


def monitor_databases(
    db_paths: Iterable[Path],
    analytics_db: Path,
    *,
    interval: int = 60,
    cycles: int = 1,
    threshold: int = 100,
) -> None:
    """Periodically record metrics for ``db_paths``."""
    paths = [Path(p) for p in db_paths]
    cycle = 0
    while cycles == 0 or cycle < cycles:
        collect_metrics(paths, analytics_db, threshold=threshold)
        cycle += 1
        if cycles == 0 or cycle < cycles:
            time.sleep(interval)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Database event monitor")
    parser.add_argument(
        "--database",
        nargs="+",
        type=Path,
        default=[
            Path("databases/production.db"),
            Path("databases/analytics.db"),
            Path("databases/template_intelligence.db"),
        ],
        help="Paths to databases",
    )
    parser.add_argument(
        "--analytics",
        type=Path,
        default=Path("databases/analytics.db"),
        help="Path to analytics database",
    )
    parser.add_argument("--interval", type=int, default=60)
    parser.add_argument("--cycles", type=int, default=1)
    parser.add_argument("--threshold", type=int, default=100)

    args = parser.parse_args()
    setup_enterprise_logging()
    monitor_databases(
        args.database,
        args.analytics,
        interval=args.interval,
        cycles=args.cycles,
        threshold=args.threshold,
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

