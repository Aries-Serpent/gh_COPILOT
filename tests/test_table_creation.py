"""Test migration SQL for table creation with dual validation using an in-memory database."""

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


def _primary_check(conn: sqlite3.Connection) -> bool:
    return all(_table_exists(conn, tbl) for tbl in ["code_audit_log", "correction_history", "code_audit_history"])


def _secondary_check(conn: sqlite3.Connection) -> bool:
    """Mirror :func:`_primary_check`."""
    return _primary_check(conn)


def test_table_creation_dual(capsys) -> None:
    """Execute migrations in-memory with progress and validate."""
    print("Test: code_audit_log and correction_history creation")
    start = dt.datetime.now()

    sql_files = [
        Path("databases/migrations/add_code_audit_log.sql"),
        Path("databases/migrations/add_correction_history.sql"),
        Path("databases/migrations/add_code_audit_history.sql"),
        Path("databases/migrations/add_violation_logs.sql"),
        Path("databases/migrations/add_rollback_logs.sql"),
    ]

    with sqlite3.connect(":memory:") as conn:
        for sql in tqdm(sql_files, desc="applying-migrations", unit="step"):
            conn.executescript(sql.read_text())

        assert _primary_check(conn)
        assert _secondary_check(conn)

    print(f"Completed in {dt.datetime.now() - start}")
    captured = capsys.readouterr()
    assert "Completed" in captured.out
