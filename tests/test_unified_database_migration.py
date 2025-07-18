import sqlite3
from pathlib import Path

import pytest

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


def test_default_sources_from_documentation(tmp_path: Path) -> None:
    databases_dir = tmp_path / "databases"
    docs_dir = tmp_path / "documentation"
    databases_dir.mkdir()
    docs_dir.mkdir()

    source_names = ["source1.db", "source2.db"]
    for name in source_names:
        with sqlite3.connect(databases_dir / name) as conn:
            conn.execute("CREATE TABLE t(id INTEGER)")
            conn.execute("INSERT INTO t VALUES (1)")

    list_file = docs_dir / "CONSOLIDATED_DATABASE_LIST.md"
    list_file.write_text("\n".join(f"- {name}" for name in source_names))

    run_migration(tmp_path)

    enterprise_db = databases_dir / "enterprise_assets.db"
    with sqlite3.connect(enterprise_db) as conn:
        ops = [row[0] for row in conn.execute(
            "SELECT operation FROM cross_database_sync_operations"
        )]
    for name in source_names:
        assert any(f"start_migrate_{name}" == op for op in ops)
        assert any(f"completed_migrate_{name}" == op for op in ops)
