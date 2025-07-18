import sqlite3
from pathlib import Path

from scripts.database.unified_database_migration import run_migration


def test_run_migration_creates_db(tmp_path: Path) -> None:
    databases = tmp_path / "databases"
    databases.mkdir()
    run_migration(tmp_path, sources=[], compression_first=True)
    db_path = databases / "enterprise_assets.db"
    assert db_path.exists()
    with sqlite3.connect(db_path) as conn:
        tables = [row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )]
    assert "cross_database_sync_operations" in tables


def test_run_migration_monitor_size(tmp_path: Path) -> None:
    databases = tmp_path / "databases"
    databases.mkdir()
    run_migration(tmp_path, sources=[], compression_first=True, monitor_size=True)
    db_path = databases / "enterprise_assets.db"
    assert db_path.exists()
