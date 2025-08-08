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


def test_production_db_has_code_templates_table() -> None:
    """The production database should include the code_templates table."""
    db_path = Path("databases/production.db")
    with sqlite3.connect(db_path) as conn:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    assert "code_templates" in tables

