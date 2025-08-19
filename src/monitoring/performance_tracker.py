#!/usr/bin/env python3
"""Performance tracking utilities for ``analytics.db``.

The module now supports optional connection reuse for high-frequency
metric ingestion.  Passing an open :class:`sqlite3.Connection` avoids the
overhead of repeatedly creating and closing connections when logging
metrics in tight loops.
"""

import asyncio
import builtins
import logging
import os
import sqlite3
import threading
from pathlib import Path
from time import perf_counter, sleep
from typing import Dict, Iterable, Optional

from .quantum_score import quantum_score

WORKSPACE_ROOT = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
DB_PATH = WORKSPACE_ROOT / "analytics.db"

WEB_DASHBOARD_ENABLED = os.getenv("WEB_DASHBOARD_ENABLED") == "1"

RESPONSE_TIME_ALERT_MS = 100.0
ERROR_RATE_ALERT = 0.05
ANOMALY_DEVIATION = 25.0

logger = logging.getLogger(__name__)

__all__ = [
    "track_query_time",
    "record_error",
    "ensure_table",
    "benchmark_queries",
    "benchmark_queries_async",
    "push_metrics",
    "benchmark_metric_overhead",
    "schedule_metrics_push",
    "RESPONSE_TIME_ALERT_MS",
    "ERROR_RATE_ALERT",
    "ml_anomaly_detect",
    "quantum_hook",
]


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
    metrics = {
        "avg_response_time_ms": avg_response,
        "error_rate": error_rate,
        "within_time_target": avg_response < 50.0,
        "within_error_target": error_rate < 0.01,
        "response_time_alert": avg_response > RESPONSE_TIME_ALERT_MS,
        "error_rate_alert": error_rate > ERROR_RATE_ALERT,
    }
    metrics["ml_anomaly"] = ml_anomaly_detect(metrics)
    quantum_hook(metrics)
    return metrics


def ml_anomaly_detect(metrics: Dict[str, float]) -> bool:
    """Naive ML-based anomaly detector for performance metrics."""

    values = [metrics["avg_response_time_ms"], metrics["error_rate"] * 100]
    avg = sum(values) / len(values)
    return any(abs(v - avg) > ANOMALY_DEVIATION for v in values)


def quantum_hook(metrics: Dict[str, float]) -> float:
    """Compute a quantum-inspired score for performance metrics."""

    values = [metrics["avg_response_time_ms"], metrics["error_rate"] * 100]
    score = quantum_score(values)
    metrics["quantum_score"] = score
    return score


def _update_dashboard(metrics: Dict[str, float]) -> None:
    if WEB_DASHBOARD_ENABLED:
        logger.info("[DASHBOARD] %s", metrics)


def track_query_time(
    query_name: str,
    duration_ms: float,
    db_path: Optional[Path] = None,
    conn: Optional[sqlite3.Connection] = None,
    commit: bool = True,
) -> Dict[str, float]:
    """Record a query's response time and return aggregate metrics.

    Reusing an existing ``conn`` allows batching of inserts for better
    throughput under heavy load.
    """
    path = db_path or DB_PATH
    if conn is None:
        with sqlite3.connect(path) as conn:  # pragma: no cover - exercised in tests
            _ensure_table(conn)
            conn.execute(
                "INSERT INTO query_performance (query_name, response_time_ms) VALUES (?, ?)",
                (query_name, duration_ms),
            )
            conn.commit()
            metrics = _compute_metrics(conn)
    else:
        _ensure_table(conn)
        conn.execute(
            "INSERT INTO query_performance (query_name, response_time_ms) VALUES (?, ?)",
            (query_name, duration_ms),
        )
        if commit:
            conn.commit()
        metrics = _compute_metrics(conn)
    _update_dashboard(metrics)
    return metrics


def record_error(
    query_name: str,
    db_path: Optional[Path] = None,
    conn: Optional[sqlite3.Connection] = None,
    commit: bool = True,
) -> Dict[str, float]:
    """Record an error occurrence for a query and return aggregate metrics."""
    path = db_path or DB_PATH
    if conn is None:
        with sqlite3.connect(path) as conn:  # pragma: no cover - exercised in tests
            _ensure_table(conn)
            conn.execute(
                "INSERT INTO query_performance (query_name, response_time_ms, is_error) VALUES (?, 0, 1)",
                (query_name,),
            )
            conn.commit()
            metrics = _compute_metrics(conn)
    else:
        _ensure_table(conn)
        conn.execute(
            "INSERT INTO query_performance (query_name, response_time_ms, is_error) VALUES (?, 0, 1)",
            (query_name,),
        )
        if commit:
            conn.commit()
        metrics = _compute_metrics(conn)
    _update_dashboard(metrics)
    return metrics


def benchmark_queries(queries: Iterable[str], db_path: Optional[Path] = None) -> Dict[str, float]:
    """Execute queries while tracking performance metrics.

    The function now reuses a single connection for the entire benchmark
    run which significantly reduces overhead compared to opening a new
    connection for each query.
    """
    metrics: Dict[str, float] = {}
    path = db_path or DB_PATH
    with sqlite3.connect(path) as conn:
        _ensure_table(conn)
        for query in queries:
            start = perf_counter()
            try:
                conn.execute(query)
            except sqlite3.Error as exc:
                logger.error("Query failed: %s", exc)
                metrics = record_error(query, db_path=path, conn=conn, commit=False)
            else:
                duration = (perf_counter() - start) * 1000
                metrics = track_query_time(query, duration, db_path=path, conn=conn, commit=False)
        conn.commit()
    return metrics


async def benchmark_queries_async(
    queries: Iterable[str], db_path: Optional[Path] = None
) -> Dict[str, float]:
    """Asynchronous variant of :func:`benchmark_queries`."""

    loop = asyncio.get_running_loop()
    metrics: Dict[str, float] = {}
    path = db_path or DB_PATH
    with sqlite3.connect(path, check_same_thread=False) as conn:
        _ensure_table(conn)
        for query in queries:
            start = perf_counter()
            try:
                await loop.run_in_executor(None, conn.execute, query)
            except sqlite3.Error as exc:
                logger.error("Query failed: %s", exc)
                metrics = record_error(query, db_path=path, conn=conn, commit=False)
            else:
                duration = (perf_counter() - start) * 1000
                metrics = track_query_time(
                    query, duration, db_path=path, conn=conn, commit=False
                )
        conn.commit()
    return metrics


async def benchmark_metric_overhead(
    samples: int = 100, db_path: Optional[Path] = None
) -> float:
    """Return the average time in milliseconds to log a metric asynchronously."""

    loop = asyncio.get_running_loop()
    path = db_path or DB_PATH
    durations = []
    with sqlite3.connect(path, check_same_thread=False) as conn:
        _ensure_table(conn)
        for i in range(samples):
            start = perf_counter()
            await loop.run_in_executor(
                None,
                track_query_time,
                f"bench{i}",
                1.0,
                path,
                conn,
                False,
            )
            durations.append((perf_counter() - start) * 1000)
        conn.commit()
    return sum(durations) / len(durations)


def push_metrics(db_path: Optional[Path] = None) -> Dict[str, float]:
    """Compute aggregate metrics and store them in ``analytics.db``."""

    path = db_path or DB_PATH
    with sqlite3.connect(path) as conn:
        _ensure_table(conn)
        metrics = _compute_metrics(conn)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS performance_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                avg_response_time_ms REAL,
                error_rate REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            "INSERT INTO performance_summary (avg_response_time_ms, error_rate) VALUES (?, ?)",
            (metrics["avg_response_time_ms"], metrics["error_rate"]),
        )
        conn.commit()
    _update_dashboard(metrics)
    return metrics


def schedule_metrics_push(
    interval: float, db_path: Optional[Path] = None, stop_event: Optional[threading.Event] = None
) -> threading.Thread:
    """Periodically push performance metrics to ``analytics.db``."""

    def _loop() -> None:
        while stop_event is None or not stop_event.is_set():
            push_metrics(db_path=db_path)
            if stop_event is None:  # pragma: no cover - infinite loop when None
                sleep(interval)
            else:
                stop_event.wait(interval)

    thread = threading.Thread(target=_loop, daemon=True)
    thread.start()
    return thread


builtins.benchmark_queries = benchmark_queries
