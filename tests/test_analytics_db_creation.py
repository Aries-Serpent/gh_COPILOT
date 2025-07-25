import sqlite3
from pathlib import Path

MIGRATIONS = [
    Path("databases/migrations/add_code_audit_log.sql"),
    Path("databases/migrations/add_correction_history.sql"),
]


def run_migrations(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        for sql_file in MIGRATIONS:
            conn.executescript(sql_file.read_text())


def table_exists(conn: sqlite3.Connection, name: str) -> bool:
    return (
        conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (name,),
        ).fetchone()
        is not None
    )


def test_analytics_db_creation(tmp_path: Path) -> None:
    db_file = tmp_path / "analytics.db"
    run_migrations(db_file)
    with sqlite3.connect(db_file) as conn:
        assert table_exists(conn, "code_audit_log")
        assert table_exists(conn, "correction_history")
