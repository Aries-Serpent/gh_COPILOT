import os
import sqlite3
from pathlib import Path

from deployment.scripts import (
    backup_manager,
    data_migration,
    environment_migration,
    quantum_backup,
    quantum_migration,
    restoration_engine,
)


def _create_temp_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE t(x INTEGER)")
    conn.close()


def test_environment_migration_supports_new_db(tmp_path, monkeypatch):
    db_path = tmp_path / "new.db"
    _create_temp_db(db_path)
    monkeypatch.setitem(environment_migration.SUPPORTED_DATABASES, "newdb", db_path)

    processed = environment_migration.migrate_environment(["newdb"])
    assert processed == ["newdb"]


def test_backup_and_restore(tmp_path, monkeypatch):
    db_path = tmp_path / "source.db"
    _create_temp_db(db_path)
    monkeypatch.setitem(environment_migration.SUPPORTED_DATABASES, "sourcedb", db_path)

    backup_dir = tmp_path / "backups"
    backup_path = backup_manager.create_backup("sourcedb", backup_root=backup_dir)
    assert backup_path.exists()

    os.remove(db_path)
    restoration_engine.restore_backup("sourcedb", backup_root=backup_dir)
    assert db_path.exists()


def test_quantum_helpers(tmp_path, monkeypatch):
    q_db = tmp_path / "ghc_quantum.db"
    _create_temp_db(q_db)
    monkeypatch.setitem(environment_migration.SUPPORTED_DATABASES, "quantum", q_db)

    assert quantum_migration.migrate_quantum() == ["quantum"]
    assert data_migration.migrate_data("quantum", "quantum") == ("quantum", "quantum")

    backup_dir = tmp_path / "qbackups"
    backup = quantum_backup.backup_quantum(backup_root=backup_dir)
    assert backup.exists()
