"""Tests for backup and restoration utilities."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from deployment.scripts.environment_migration import (
    SUPPORTED_DATABASES,
    get_registered_databases,
    register_database,
    validate_database_file,
)
from deployment.scripts.backup_manager import create_backup, restore_backup


def test_backup_and_restore_roundtrip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Database can be backed up and restored successfully."""

    db_path = tmp_path / "sample.db"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE t(x INTEGER);")
    conn.commit()
    conn.close()

    register_database("sample", db_path)
    assert "sample" in get_registered_databases()

    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path))

    backup_file = create_backup("sample")
    assert backup_file.exists()

    db_path.unlink()
    assert not db_path.exists()

    restore_backup("sample")
    assert db_path.exists()
    validate_database_file(db_path)

    SUPPORTED_DATABASES.pop("sample", None)

