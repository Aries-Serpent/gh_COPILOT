from __future__ import annotations

"""Simple recovery helpers for monitoring routines.

This module ties recovery actions to anomaly detection (Task 19) and
session validation checks (Task 20).  It reacts to three situations:

* database disconnects
* cache misses
* log saturation

The implementation intentionally keeps the logic minimal while providing
hooks that other modules can integrate with.
"""

from pathlib import Path
from typing import Any, Callable, Dict, Iterable
import sqlite3

from src.monitoring import anomaly
from src.session import validators


def recover_system(
    models: Dict[str, anomaly.Model],
    metrics: Dict[str, float],
    connections: Iterable[sqlite3.Connection],
    conn_factory: Callable[[], sqlite3.Connection],
    cache: Dict[str, Any],
    cache_loader: Callable[[], Dict[str, Any]],
    log_dir: Path,
    *,
    log_limit: int = 1000,
) -> Dict[str, int]:
    """Apply recovery routines based on detected anomalies.

    Parameters
    ----------
    models:
        Baseline anomaly detection models.
    metrics:
        Current metric readings to evaluate.
    connections:
        Existing database connections that may require validation.
    conn_factory:
        Callable that produces a new ``sqlite3.Connection``.
    cache:
        Mutable mapping used as a simple cache.
    cache_loader:
        Callable returning fresh cache data when a miss occurs.
    log_dir:
        Directory containing ``*.log`` files to monitor for saturation.
    log_limit:
        Maximum allowed size (in bytes) for a log file.

    Returns
    -------
    Dict[str, int]
        Counts of performed recovery actions with keys ``db_reconnects``,
        ``cache_refreshes`` and ``log_truncations``.
    """

    actions = {"db_reconnects": 0, "cache_refreshes": 0, "log_truncations": 0}

    anomalies = anomaly.detect_anomalies(models, metrics)

    if anomalies.get("db_disconnects"):
        open_conns = validators.check_open_connections(list(connections))
        closed_count = len(list(connections)) - len(open_conns)
        for _ in range(closed_count):
            try:
                conn_factory()
            except Exception:  # pragma: no cover - defensive
                continue
            actions["db_reconnects"] += 1

    if anomalies.get("cache_miss") and not cache:
        cache.update(cache_loader())
        actions["cache_refreshes"] += 1

    if anomalies.get("log_saturation"):
        for log_file in Path(log_dir).glob("*.log"):
            if log_file.stat().st_size > log_limit:
                log_file.write_text("")
                actions["log_truncations"] += 1
        validators.check_logs(log_dir)

    return actions


__all__ = ["recover_system"]
