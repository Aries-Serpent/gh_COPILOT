import sqlite3
from pathlib import Path

from scripts.database.unified_database_initializer import initialize_database


def test_initializer_creates_tables(tmp_path: Path) -> None:
    db_path = tmp_path / "enterprise_assets.db"
    initialize_database(db_path)
    with sqlite3.connect(db_path) as conn:
        tables = set(
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        )
    expected = {
        "script_assets",
        "documentation_assets",
        "template_assets",
        "pattern_assets",
        "enterprise_metadata",
        "integration_tracking",
        "cross_database_sync_operations",
    }
    assert expected.issubset(tables)
