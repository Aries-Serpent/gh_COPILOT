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

    archive = export_table_to_7z(db, "t", tmp_path)
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
        migrate_and_compress(tmp_path, [big_db.name, small_db.name])

    assert enterprise_db.exists()
    archive = tmp_path / "archives" / "table_exports" / f"{enterprise_db.stem}_bigtable.7z"
    assert archive.exists()
    with py7zr.SevenZipFile(archive, "r") as zf:
        names = zf.getnames()
    assert any(name.endswith("bigtable.csv") for name in names)

    with sqlite3.connect(enterprise_db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM smalltable").fetchone()[0] == 10
        assert conn.execute("SELECT COUNT(*) FROM bigtable").fetchone()[0] == 60000


def test_migrate_and_compress_rollback_on_failure(tmp_path: Path, monkeypatch) -> None:
    db_dir = tmp_path / "databases"
    db_dir.mkdir()

    first = db_dir / "first.db"
    second = db_dir / "second.db"
    _create_db(first, "t1", 5)
    _create_db(second, "t2", 5)

    enterprise_db = db_dir / "enterprise_assets.db"

    call_count = {"n": 0}

    def failing_migrate(self):
        if call_count["n"]:
            with sqlite3.connect(self.target_db) as conn:
                conn.execute("CREATE TABLE t2 (id INTEGER)")
                conn.execute("INSERT INTO t2 (id) VALUES (1)")
                conn.commit()
            raise RuntimeError("failure")
        call_count["n"] += 1
        with sqlite3.connect(self.target_db) as tgt, sqlite3.connect(self.source_db) as src:
            for tbl, in src.execute("SELECT name FROM sqlite_master WHERE type='table'"):
                tgt.execute(f"CREATE TABLE {tbl} (id INTEGER)")
                rows = src.execute(f"SELECT id FROM {tbl}").fetchall()
                tgt.executemany(f"INSERT INTO {tbl} VALUES (?)", rows)
            tgt.commit()

    monkeypatch.setattr(DatabaseMigrationCorrector, "migrate_database_content", failing_migrate)

    with pytest.raises(RuntimeError):
        migrate_and_compress(tmp_path, [first.name, second.name])

    with sqlite3.connect(enterprise_db) as conn:
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        assert "t1" in tables
        assert "t2" not in tables

    log_file = tmp_path / "logs" / "rollback.log"
    assert log_file.exists()
    assert "second.db" in log_file.read_text()
