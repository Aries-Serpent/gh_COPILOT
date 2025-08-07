from pathlib import Path
import sqlite3


def test_production_db_accessible() -> None:
    """Ensure the production database can be queried."""
    db_path = Path("databases/production.db")
    with sqlite3.connect(db_path) as conn:
        conn.execute("SELECT 1")


def test_production_db_has_tables() -> None:
    """Production database should contain at least one table."""
    db_path = Path("databases/production.db")
    with sqlite3.connect(db_path) as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    assert tables

