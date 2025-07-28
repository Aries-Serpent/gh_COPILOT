import os
import shutil
import sqlite3
from pathlib import Path

import pytest

from scripts.file_management.autonomous_file_manager import AutonomousFileManager


def setup_db(db_path: Path, file_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO enhanced_script_tracking (script_path, script_content, script_hash, script_type, functionality_category) VALUES (?, ?, ?, ?, ?)",
            (
                str(file_path),
                "pass",
                "dummyhash",
                "utility",
                "tests",
            ),
        )


def test_organize_files_moves_and_updates(tmp_path):
    workspace = tmp_path
    db_dir = workspace / "databases"
    db_dir.mkdir()
    db = db_dir / "production.db"
    shutil.copy(Path("databases/production.db"), db)

    file_path = workspace / "sample.py"
    file_path.write_text("pass")
    setup_db(db, file_path)

    os.environ["GH_COPILOT_WORKSPACE"] = str(workspace)
    os.environ["GH_COPILOT_BACKUP_ROOT"] = str(tmp_path.parent / "backups")

    manager = AutonomousFileManager(db)
    manager.organize_files(workspace)

    dest = workspace / "organized" / "tests" / "utility" / "sample.py"
    assert dest.exists()

    with sqlite3.connect(db) as conn:
        cur = conn.execute(
            "SELECT script_path FROM enhanced_script_tracking WHERE script_type='utility'"
        )
        assert cur.fetchone()[0] == str(dest)


def test_organize_files_rejects_backup(tmp_path):
    workspace = tmp_path / "ws"
    backup = tmp_path / "backups"
    workspace.mkdir()
    backup.mkdir()
    db_dir = workspace / "databases"
    db_dir.mkdir()
    db = db_dir / "production.db"
    shutil.copy(Path("databases/production.db"), db)

    os.environ["GH_COPILOT_WORKSPACE"] = str(workspace)
    os.environ["GH_COPILOT_BACKUP_ROOT"] = str(backup)

    manager = AutonomousFileManager(db)
    with pytest.raises(RuntimeError):
        manager.organize_files(backup)
