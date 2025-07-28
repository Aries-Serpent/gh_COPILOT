#!/usr/bin/env python3
"""Performance tracking utilities for analytics.db."""

import builtins
import logging
import os
import sqlite3
from pathlib import Path
from time import perf_counter
from typing import Dict, Iterable, Optional

WORKSPACE_ROOT = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
DB_PATH = WORKSPACE_ROOT / "analytics.db"

WEB_DASHBOARD_ENABLED = os.getenv("WEB_DASHBOARD_ENABLED") == "1"

logger = logging.getLogger(__name__)

__all__ = ["track_query_time", "record_error", "ensure_table", "benchmark_queries"]


def _ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS query_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query_name TEXT NOT NULL,
            response_time_ms REAL NOT NULL,
            is_error INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def ensure_table(conn: sqlite3.Connection) -> None:
    """Public wrapper to ensure query performance table exists."""
    _ensure_table(conn)


def _compute_metrics(conn: sqlite3.Connection) -> Dict[str, float]:
    cur = conn.execute("SELECT AVG(response_time_ms) FROM query_performance WHERE is_error = 0")
    avg_response = cur.fetchone()[0] or 0.0
    cur = conn.execute("SELECT SUM(is_error), COUNT(*) FROM query_performance")
    errors, total = cur.fetchone()
    error_rate = (errors or 0) / total if total else 0.0
    return {
        "avg_response_time_ms": avg_response,
        "error_rate": error_rate,
        "within_time_target": avg_response < 50.0,
        "within_error_target": error_rate < 0.01,
    }


def _update_dashboard(metrics: Dict[str, float]) -> None:
    if WEB_DASHBOARD_ENABLED:
        logger.info("[DASHBOARD] %s", metrics)


def track_query_time(query_name: str, duration_ms: float, db_path: Optional[Path] = None) -> Dict[str, float]:
    """Record a query's response time and return aggregate metrics."""
    path = db_path or DB_PATH
    with sqlite3.connect(path) as conn:
        _ensure_table(conn)
        conn.execute(
            "INSERT INTO query_performance (query_name, response_time_ms) VALUES (?, ?)",
            (query_name, duration_ms),
        )
        conn.commit()
        metrics = _compute_metrics(conn)
    _update_dashboard(metrics)
    return metrics


def record_error(query_name: str, db_path: Optional[Path] = None) -> Dict[str, float]:
    """Record an error occurrence for a query and return aggregate metrics."""
    path = db_path or DB_PATH
    with sqlite3.connect(path) as conn:
        _ensure_table(conn)
        conn.execute(
            "INSERT INTO query_performance (query_name, \
                response_time_ms, is_error) VALUES (?, 0, 1)",
            (query_name,),
        )
        conn.commit()
        metrics = _compute_metrics(conn)
    _update_dashboard(metrics)
    return metrics


def benchmark_queries(queries: Iterable[str], db_path: Optional[Path] = None) -> Dict[str, float]:
    """Execute queries while tracking performance metrics."""
    metrics: Dict[str, float] = {}
    path = db_path or DB_PATH
    for query in queries:
        start = perf_counter()
        try:
            with sqlite3.connect(path) as conn:
                conn.execute(query)
        except sqlite3.Error as exc:
            logger.error("Query failed: %s", exc)
            metrics = record_error(query, db_path=path)
        else:
            duration = (perf_counter() - start) * 1000
            metrics = track_query_time(query, duration, db_path=path)
    return metrics


builtins.benchmark_queries = benchmark_queries
