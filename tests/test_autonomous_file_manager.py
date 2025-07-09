import sqlite3
import tempfile
from pathlib import Path

from copilot.core.autonomous_file_manager import (
    AutonomousFileManager,
    IntelligentFileClassifier,
    AutonomousBackupManager,
)

import pytest


def _setup_db(db_path: Path, base: Path) -> None:
    """Create a minimal production.db used by the tests."""
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS scripts (
            script_path TEXT,
            category TEXT,
            script_type TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS enhanced_script_tracking (
            script_path TEXT,
            functionality_category TEXT,
            script_type TEXT,
            backup_score INTEGER,
            last_modified TEXT
        )
        """
    )
    conn.executemany(
        "INSERT INTO scripts VALUES (?, ?, ?)",
        [
            (str(base / "a.py"), "utilities", "python"),
            (str(base / "b.sh"), "scripts", "bash"),
        ]
    )
    conn.executemany(
        "INSERT INTO enhanced_script_tracking VALUES (?, ?, ?, ?, ?)",
        [
            (str(base / "a.py"), "utilities", "python", 80, "2021-01-01"),
            (str(base / "b.sh"), "scripts", "bash", 60, "2021-01-02"),
        ]
    )
    conn.commit()
    conn.close()


def test_organize_files_autonomously(tmp_path, monkeypatch):
    db = tmp_path / "production.db"
    _setup_db(db, tmp_path)

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    mgr = AutonomousFileManager()
    result = mgr.organize_files_autonomously([str(tmp_path / "foo.py"), str(tmp_path / "bar.sh")])

    assert result[str(tmp_path / "foo.py")] == str(tmp_path / "utilities" / "foo.py")
    assert result[str(tmp_path / "bar.sh")] == str(tmp_path / "scripts" / "bar.sh")


def test_classify_file_autonomously(tmp_path, monkeypatch):
    db = tmp_path / "production.db"
    _setup_db(db, tmp_path)

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    classifier = IntelligentFileClassifier()
    info = classifier.classify_file_autonomously(str(tmp_path / "a.py"))

    assert info["category"] == "utilities"
    assert info["type"] == "python"
    assert info["confidence"] == 1.0


def test_create_intelligent_backup(tmp_path, monkeypatch):
    db = tmp_path / "production.db"
    _setup_db(db, tmp_path)

    (tmp_path / "a.py").write_text("print('a')")
    (tmp_path / "b.sh").write_text("echo b")

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    mgr = AutonomousBackupManager()
    backup_root = Path(tempfile.mkdtemp())
    monkeypatch.setattr(mgr, "backup_root", backup_root)

    dest = mgr.create_intelligent_backup(file_priority="LOW")
    dest_path = Path(dest)

    assert (dest_path / "a.py").is_file()
    assert (dest_path / "b.sh").is_file()