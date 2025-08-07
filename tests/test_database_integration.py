from pathlib import Path
import sqlite3


def test_production_db_accessible() -> None:
    """Ensure the production database can be queried."""
    db_path = Path("databases/production.db")
    with sqlite3.connect(db_path) as conn:
        conn.execute("SELECT 1")

