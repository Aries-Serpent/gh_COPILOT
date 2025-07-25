#!/usr/bin/env python3
"""Dry-run tester for analytics.db migrations.

This script simulates executing the analytics database migrations
(`add_code_audit_log.sql` and `add_correction_history.sql`) in an
in-memory SQLite database. It demonstrates the database-first pattern
by querying ``production.db`` for a sanity check before running the
migration SQL. The Dual Copilot pattern is implemented via primary and
secondary validation functions which confirm that the new tables exist.

Running this script **does not** create ``analytics.db``. It merely
verifies that the migrations could be applied successfully.
"""
from __future__ import annotations

import datetime as dt
import os
import sqlite3
from pathlib import Path

from tqdm import tqdm

WORKSPACE = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
PRODUCTION_DB = WORKSPACE / "databases" / "production.db"
MIGRATIONS = [
    WORKSPACE / "databases" / "migrations" / "add_code_audit_log.sql",
    WORKSPACE / "databases" / "migrations" / "add_correction_history.sql",
    WORKSPACE / "databases" / "migrations" / "add_code_audit_history.sql",
]


def _database_first_check() -> bool:
    """Verify ``production.db`` is accessible and contains tables."""
    if not PRODUCTION_DB.exists():
        return False
    with sqlite3.connect(PRODUCTION_DB) as conn:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
        return cur.fetchone() is not None


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    )
    return cur.fetchone() is not None


def _primary_validation(conn: sqlite3.Connection) -> bool:
    return all(
        _table_exists(conn, t)
        for t in ("code_audit_log", "correction_history", "code_audit_history")
    )


def _secondary_validation(conn: sqlite3.Connection) -> bool:
    """Secondary validation mirroring :func:`_primary_validation`."""
    return _primary_validation(conn)


def run() -> bool:
    """Simulate migrations with progress indicators."""
    print("Test: Simulate analytics.db migration (dry-run)")
    start = dt.datetime.now()
    assert _database_first_check(), "production.db sanity check failed"
    with sqlite3.connect(":memory:") as conn:
        for sql in tqdm(MIGRATIONS, desc="Simulating migration steps", unit="step"):
            conn.executescript(sql.read_text())
        assert _primary_validation(conn)
        assert _secondary_validation(conn)
    print(f"Completed simulation in {dt.datetime.now() - start}")
    return True


if __name__ == "__main__":  # pragma: no cover - manual invocation
    success = run()
    raise SystemExit(0 if success else 1)
