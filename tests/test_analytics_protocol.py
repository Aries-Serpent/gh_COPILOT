"""Dry-run analytics migrations using an in-memory SQLite database."""

import datetime as dt
import os
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
    return all(_table_exists(conn, tbl) for tbl in ["code_audit_log", "correction_history"])


def _secondary_validation(conn: sqlite3.Connection) -> bool:
    return _primary_validation(conn)


def test_analytics_protocol_dry_run(capsys) -> None:
    analytics_db = Path("databases/analytics.db")
    mtime = analytics_db.stat().st_mtime

    print("Test: Dry-run analytics.db migrations")
    print(f"Start: {dt.datetime.now()}")
    print(f"PID: {os.getpid()}")
    start = dt.datetime.now()

    migration_files = [
        Path("databases/migrations/add_code_audit_log.sql"),
        Path("databases/migrations/add_correction_history.sql"),
        Path("databases/migrations/add_code_audit_history.sql"),
        Path("databases/migrations/add_violation_logs.sql"),
        Path("databases/migrations/add_rollback_logs.sql"),
        Path("databases/migrations/add_placeholder_removals.sql"),
        Path("databases/migrations/add_size_violations.sql"),
    ]

    with sqlite3.connect(":memory:") as conn:
        for sql in tqdm(migration_files, desc="Simulating migration steps", unit="step"):
            conn.executescript(sql.read_text())

        assert _primary_validation(conn)
        assert _secondary_validation(conn)

    print(f"Completed simulation in {dt.datetime.now() - start}")
    captured = capsys.readouterr()
    assert "Completed simulation" in captured.out
    assert analytics_db.stat().st_mtime == mtime
