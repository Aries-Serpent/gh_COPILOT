"""Failure recovery routines.

This module provides simple handlers that attempt to recover from
transient issues.  It includes database reconnection logic, sync retry
helpers and integration hooks for monitoring alerts.
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, Iterable

import sqlite3

from monitoring import anomaly
from session import validators


def reconnect_database(
    factory: Callable[[], sqlite3.Connection],
    *,
    attempts: int = 3,
    delay: float = 0.1,
) -> sqlite3.Connection:
    """Return a database connection using ``factory`` with retries.

    The ``factory`` callable is invoked until it succeeds or ``attempts``
    are exhausted.  ``delay`` specifies the pause between attempts in
    seconds.
    """

    last_exc: Exception | None = None
    for _ in range(attempts):
        try:
            return factory()
        except Exception as exc:  # pragma: no cover - defensive
            last_exc = exc
            time.sleep(delay)
    assert last_exc is not None  # for mypy
    raise last_exc


def retry_sync(
    action: Callable[[], Any],
    *,
    attempts: int = 3,
    delay: float = 0.1,
) -> Any:
    """Execute ``action`` with retry semantics.

    The ``action`` callable is invoked until it completes without
    raising an exception or ``attempts`` are exhausted.  The result of
    the successful invocation is returned.
    """

    last_exc: Exception | None = None
    for _ in range(attempts):
        try:
            return action()
        except Exception as exc:
            last_exc = exc
            time.sleep(delay)
    assert last_exc is not None  # for mypy
    raise last_exc


def handle_alerts(
    models: Dict[str, anomaly.Model],
    metrics: Dict[str, float],
    connections: Iterable[sqlite3.Connection],
    conn_factory: Callable[[], sqlite3.Connection],
    sync_action: Callable[[], Any],
) -> Dict[str, int]:
    """Trigger recovery routines based on monitoring alerts.

    Returns a mapping with counts of performed actions.  A sync retry is
    attempted when anomalies are detected by
    :func:`monitoring.anomaly.detect_anomalies`.  Open connections
    reported by :func:`session.validators.check_open_connections`
    trigger database reconnection attempts using ``conn_factory``.
    """

    counts = {"reconnects": 0, "sync_retries": 0}

    anomalies = anomaly.detect_anomalies(models, metrics)
    if any(anomalies.values()):
        retry_sync(sync_action)
        counts["sync_retries"] += 1

    open_conns = validators.check_open_connections(list(connections))
    for _ in open_conns:
        reconnect_database(conn_factory)
        counts["reconnects"] += 1

    return counts


__all__ = ["reconnect_database", "retry_sync", "handle_alerts"]
