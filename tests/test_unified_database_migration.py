import sqlite3
from pathlib import Path

from scripts.database.unified_database_migration import run_migration


def _create_db(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE t (id INTEGER)")
        conn.executemany("INSERT INTO t (id) VALUES (?)", [(i,) for i in range(5)])
        conn.commit()


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


def test_run_migration_creates_backup(tmp_path: Path, monkeypatch) -> None:
    databases = tmp_path / "databases"
    databases.mkdir()
    src = databases / "sample.db"
    _create_db(src)

    backup_root = tmp_path / "external"
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))

    run_migration(tmp_path, sources=[src.name], compression_first=True)

    backup_dir = backup_root / "database_consolidation"
    backups = list(backup_dir.glob("sample_*.backup"))
    assert backups
    assert not str(backups[0]).startswith(str(tmp_path))
