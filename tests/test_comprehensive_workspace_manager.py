import shutil
import sqlite3
from pathlib import Path

from scripts.session.COMPREHENSIVE_WORKSPACE_MANAGER import ComprehensiveWorkspaceManager


DEFAULT_DB = Path("databases/production.db")


def copy_db(tmp_path: Path) -> Path:
    db = tmp_path / "production.db"
    shutil.copy(DEFAULT_DB, db)
    return db


def test_start_end_session_records_wrapup(tmp_path, monkeypatch):
    temp_db = copy_db(tmp_path)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    backup_root = tmp_path.parent / "backups"
    backup_root.mkdir()
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))

    zero_file = tmp_path / "zero.txt"
    zero_file.write_text("")
    rec_dir = tmp_path / "old_backup"
    rec_dir.mkdir()

    manager = ComprehensiveWorkspaceManager(db_path=temp_db, autofix=True)

    assert manager.start_session()
    assert not zero_file.exists()
    assert not rec_dir.exists()

    row_id = int(manager.session_file.read_text())
    with sqlite3.connect(temp_db) as conn:
        status, end_time = conn.execute(
            "SELECT status, end_time FROM session_wrapups WHERE id = ?",
            (row_id,),
        ).fetchone()
    assert status == "RUNNING"
    assert end_time is None

    assert manager.end_session()
    with sqlite3.connect(temp_db) as conn:
        status, end_time = conn.execute(
            "SELECT status, end_time FROM session_wrapups WHERE id = ?",
            (row_id,),
        ).fetchone()
    assert status == "COMPLETED"
    assert end_time is not None
    assert not manager.session_file.exists()

