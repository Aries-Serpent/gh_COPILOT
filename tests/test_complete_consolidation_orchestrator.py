import sqlite3
from pathlib import Path

import py7zr
import pytest

from scripts.database.complete_consolidation_orchestrator import (
    compress_large_tables,
    export_table_to_7z,
)


def test_export_table_to_7z(tmp_path: Path) -> None:
    db = tmp_path / "sample.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE t (id INTEGER)")
        conn.executemany("INSERT INTO t (id) VALUES (?)", [(i,) for i in range(5)])
        conn.commit()

    archive = export_table_to_7z(db, "t", tmp_path, level=5)
    assert archive.exists()
    with py7zr.SevenZipFile(archive, "r") as zf:
        names = zf.getnames()
    assert any(name.endswith("t.csv") for name in names)


def _create_db(path: Path, table: str, rows: int) -> None:
    if not table.isidentifier():
        raise ValueError(f"Invalid table name: {table}")
    with sqlite3.connect(path) as conn:
        if not table.isidentifier():
            raise ValueError(f"Invalid table name: {table}")
        conn.execute(f"CREATE TABLE {table} (id INTEGER)")
        conn.executemany(f"INSERT INTO {table} (id) VALUES (?)", [(i,) for i in range(rows)])
        conn.commit()


def test_migrate_and_compress_archives_large_tables(tmp_path: Path) -> None:
    db = tmp_path / "enterprise.db"
    _create_db(db, "bigtable", 60000)
    analysis = {"tables": [{"name": "bigtable", "record_count": 60000}]}

    archives = compress_large_tables(db, analysis, level=5)
    assert archives
    archive = archives[0]
    assert archive.exists()
    with py7zr.SevenZipFile(archive, "r") as zf:
        names = zf.getnames()
    assert any(name.endswith("bigtable.csv") for name in names)


def test_create_external_backup(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "test.db"
    source.write_text("data")

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    backup_root = tmp_path / "external_backups"
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))

    import importlib
    module = importlib.reload(
        importlib.import_module("scripts.database.complete_consolidation_orchestrator")
    )  # noqa: E402
    create_external_backup = module.create_external_backup

    backup = create_external_backup(source, "unit_test", backup_dir=backup_root)

    assert backup.exists()
    assert backup.parent == backup_root
    assert not str(backup).startswith(str(workspace))


def test_create_external_backup_in_workspace_raises(tmp_path: Path, monkeypatch) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    backup_root = tmp_path / "external_root"
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))
    source = workspace / "test.db"
    source.write_text("data")
    import importlib
    module = importlib.reload(
        importlib.import_module("scripts.database.complete_consolidation_orchestrator")
    )  # noqa: E402
    create_external_backup = module.create_external_backup

    with pytest.raises(RuntimeError):
        create_external_backup(source, "bad", backup_dir=workspace / "backups")
