"""Simulate analytics.db migrations without creating a file.

This test ensures that the migration SQL for ``code_audit_log`` and
``correction_history`` can execute successfully using an in-memory database.
It follows the Dual Copilot pattern and includes visual processing indicators
such as a progress bar and duration logging.
"""

from __future__ import annotations

import datetime as dt
import sqlite3
from pathlib import Path

from tqdm import tqdm


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    return (
        conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (name,),
        ).fetchone()
        is not None
    )


def _primary_validation(conn: sqlite3.Connection) -> bool:
    return all(
        _table_exists(conn, tbl) for tbl in ["code_audit_log", "correction_history"]
    )


def _secondary_validation(conn: sqlite3.Connection) -> bool:
    """Secondary check mirroring :func:`_primary_validation`."""
    return _primary_validation(conn)


def test_analytics_migration_simulation(capsys) -> None:
    """Run migrations in-memory with progress indicators."""
    print("Test: Simulate analytics.db migration (dry-run)")
    start = dt.datetime.now()

    migration_files = [
        Path("databases/migrations/add_code_audit_log.sql"),
        Path("databases/migrations/add_correction_history.sql"),
    ]

    with sqlite3.connect(":memory:") as conn:
        for sql in tqdm(migration_files, desc="Simulating migration steps", unit="step"):
            conn.executescript(sql.read_text())

        assert _primary_validation(conn)
        assert _secondary_validation(conn)

    print(f"Completed simulation in {dt.datetime.now() - start}")
    captured = capsys.readouterr()
    assert "Completed simulation" in captured.out

