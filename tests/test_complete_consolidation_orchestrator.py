import os
import sqlite3
from pathlib import Path

import pytest

# Skip tests if the optional `py7zr` dependency is unavailable
py7zr = pytest.importorskip("py7zr")

# Disable validation at import time for test isolation
os.environ.setdefault("GH_COPILOT_DISABLE_VALIDATION", "1")

from scripts.database.complete_consolidation_orchestrator import export_table_to_7z, migrate_and_compress


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


def test_migrate_and_compress_archives_large_tables(tmp_path: Path, monkeypatch) -> None:
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

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    import scripts.database.unified_database_initializer as udi

    monkeypatch.setattr(
        udi,
        "SecondaryCopilotValidator",
        lambda logger: type("Dummy", (), {"validate_corrections": lambda self, files: True})(),
    )
    with temporary_chdir(tmp_path):
        migrate_and_compress(tmp_path, [big_db.name, small_db.name], level=5)

    assert enterprise_db.exists()
    archive = tmp_path / "archives" / "table_exports" / f"{enterprise_db.stem}_bigtable.7z"
    assert archive.exists()
    with py7zr.SevenZipFile(archive, "r") as zf:
        names = zf.getnames()
    assert any(name.endswith("bigtable.csv") for name in names)


def test_create_external_backup(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "test.db"
    source.write_text("data")

    workspace = tmp_path / "ws"
    workspace.mkdir()
    internal_backup = workspace / "backups"
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))

    from scripts.database import complete_consolidation_orchestrator as cco

    with pytest.raises(RuntimeError):
        cco.create_external_backup(source, "unit_test", backup_dir=internal_backup)

    sneaky_backup = workspace / ".." / "ws" / "backups"
    with pytest.raises(RuntimeError):
        cco.create_external_backup(source, "unit_test", backup_dir=sneaky_backup)

    external_root = tmp_path / "external_backups"
    backup = cco.create_external_backup(source, "unit_test", backup_dir=external_root)

    assert backup.exists()
    assert backup.parent == external_root
    assert not str(backup).startswith(str(workspace))
