"""Lightweight helpers for placeholder snapshot queries."""

from __future__ import annotations

import sqlite3


def _ensure_placeholder_tables(conn: sqlite3.Connection) -> None:
    """Ensure minimal tables used for placeholder snapshot metrics exist."""

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS placeholder_audit_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER NOT NULL,
            open_count INTEGER NOT NULL,
            resolved_count INTEGER NOT NULL
        )
        """
    )


def get_latest_placeholder_snapshot(conn: sqlite3.Connection) -> tuple[int, int]:
    """Return the most recent ``(open, resolved)`` placeholder counts."""

    _ensure_placeholder_tables(conn)
    cur = conn.execute(
        "SELECT open_count, resolved_count FROM placeholder_audit_snapshots ORDER BY id DESC LIMIT 1"
    )
    row = cur.fetchone()
    return (int(row[0]), int(row[1])) if row else (0, 0)


__all__ = ["get_latest_placeholder_snapshot"]

