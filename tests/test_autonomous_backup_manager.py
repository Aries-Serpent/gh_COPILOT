import os
import shutil
import sqlite3
from pathlib import Path

import pytest

from scripts.file_management.autonomous_backup_manager import AutonomousBackupManager


def setup_db(workspace: Path) -> Path:
    db_dir = workspace / "databases"
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / "production.db"
    shutil.copy(Path("databases/production.db"), db_path)
    return db_path


def test_backup_created_outside_workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    db = setup_db(workspace)
    target = workspace / "data"
    target.mkdir()
    (target / "file.txt").write_text("x")

    backup_root = tmp_path / "backups"
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))

    manager = AutonomousBackupManager()
    dest = manager.create_backup(target)

    assert backup_root in dest.parents
    assert workspace not in dest.parents

    with sqlite3.connect(db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM backup_history").fetchone()[0]
    assert count == 1


def test_backup_rejects_recursive_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(workspace / "backups"))
    with pytest.raises(EnvironmentError):
        AutonomousBackupManager()
