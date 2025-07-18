import os
import sqlite3
from pathlib import Path

import py7zr
import pytest

from scripts.database.complete_consolidation_orchestrator import (
    export_table_to_7z, migrate_and_compress)
from scripts.database.database_migration_corrector import \
    DatabaseMigrationCorrector


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
    db_dir = tmp_path / "databases"
    db_dir.mkdir()

    big_db = db_dir / "big.db"
    small_db = db_dir / "small.db"
    _create_db(big_db, "bigtable", 60000)
    _create_db(small_db, "smalltable", 10)

    enterprise_db = db_dir / "enterprise_assets.db"
    from contextlib import contextmanager

    @contextmanager
    def temporary_chdir(path):
        original_cwd = os.getcwd()
        os.chdir(path)
        try:
            yield
        finally:
            os.chdir(original_cwd)

    with temporary_chdir(tmp_path):
        migrate_and_compress(tmp_path, [big_db.name, small_db.name], level=5)

    assert enterprise_db.exists()
    archive = tmp_path / "archives" / "table_exports" / f"{enterprise_db.stem}_bigtable.7z"
    assert archive.exists()
    with py7zr.SevenZipFile(archive, "r") as zf:
        names = zf.getnames()
    assert any(name.endswith("bigtable.csv") for name in names)

    with sqlite3.connect(enterprise_db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM smalltable").fetchone()[0] == 10
        assert conn.execute("SELECT COUNT(*) FROM bigtable").fetchone()[0] == 60000

    log_file = tmp_path / "migration.log"
    assert log_file.exists()
    content = log_file.read_text()
    assert "Session" in content and "ended" in content


def test_create_external_backup(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "test.db"
    source.write_text("data")

    backup_root = tmp_path / "backups"
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))

    from scripts.database.complete_consolidation_orchestrator import \
        create_external_backup

    backup = create_external_backup(source, "unit_test", backup_dir=backup_root)

    assert backup.exists()
    assert backup.parent == backup_root
    assert not str(backup).startswith(str(tmp_path))
