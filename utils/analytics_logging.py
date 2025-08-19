"""Minimal analytics logging helpers with strict TEST_MODE handling.

These functions mirror the behaviour of the existing `_log_event` helper but
provide dedicated interfaces for the project. Writes default to
``databases/analytics.db`` unless ``ANALYTICS_DB_PATH`` overrides it.

Tables are **never** created automatically in normal operation. When the
``TEST_MODE`` environment variable is set to ``1`` or ``true``, the helpers
create the minimal schema for the ``events`` and ``sync_events_log`` tables if
they are missing.
"""

from __future__ import annotations

import contextlib
import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, Optional

TEST_MODE = os.getenv("TEST_MODE", "").lower() in {"1", "true"}
DEFAULT_DB_PATH = os.getenv("ANALYTICS_DB_PATH", "databases/analytics.db")


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect(db_path: Optional[str]) -> sqlite3.Connection:
    path = db_path or DEFAULT_DB_PATH
    if not TEST_MODE and path != ":memory:" and not os.path.exists(path):
        raise RuntimeError(
            "analytics database not found; run migrations or set ANALYTICS_DB_PATH"
        )
    return sqlite3.connect(path, timeout=30)


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS events (
            event_time TEXT,
            level      TEXT,
            event      TEXT,
            details    TEXT
        );
        CREATE TABLE IF NOT EXISTS sync_events_log (
            event_time TEXT,
            file_path  TEXT,
            count      INTEGER,
            status     TEXT,
            details    TEXT
        );
        """
    )


def _json(details: Optional[Dict[str, Any]]) -> str:
    try:
        return json.dumps(details or {}, ensure_ascii=False)
    except Exception:
        return json.dumps({"_repr": repr(details)})


def log_event(
    level: str,
    event: str,
    details: Optional[Dict[str, Any]] = None,
    *,
    db_path: Optional[str] = None,
) -> bool:
    """Log a generic event.

    Returns ``True`` on success. Raises ``RuntimeError`` if the table is missing
    outside of ``TEST_MODE``.
    """

    with contextlib.ExitStack() as stack:
        conn = stack.enter_context(_connect(db_path))
        cursor = conn.cursor()
        stack.callback(cursor.close)
        if TEST_MODE:
            _ensure_schema(conn)
        try:
            cursor.execute(
                "INSERT INTO events(event_time, level, event, details) VALUES (?,?,?,?)",
                (_timestamp(), level, event, _json(details)),
            )
            return True
        except sqlite3.OperationalError as exc:  # missing table
            raise RuntimeError(
                "events table missing; run migrations or enable TEST_MODE"
            ) from exc


def log_sync_operation(
    file_path: str,
    count: int,
    status: str,
    details: Optional[Dict[str, Any]] = None,
    *,
    db_path: Optional[str] = None,
) -> bool:
    """Log the outcome of a synchronization operation."""

    with contextlib.ExitStack() as stack:
        conn = stack.enter_context(_connect(db_path))
        cursor = conn.cursor()
        stack.callback(cursor.close)
        if TEST_MODE:
            _ensure_schema(conn)
        try:
            cursor.execute(
                """
                INSERT INTO sync_events_log(event_time, file_path, count, status, details)
                VALUES (?,?,?,?,?)
                """,
                (_timestamp(), file_path, int(count), status, _json(details)),
            )
            return True
        except sqlite3.OperationalError as exc:
            raise RuntimeError(
                "sync_events_log table missing; run migrations or enable TEST_MODE"
            ) from exc


__all__ = ["log_event", "log_sync_operation"]

