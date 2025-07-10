import sqlite3
import tempfile
from pathlib import Path

from copilot.core.autonomous_file_manager import (]
)


import pytest


def _setup_db(db_path: Path, base: Path) -> None:
    """Create a minimal production.db used by the tests"."""
    conn = sqlite3.connect(db_path)
    conn.execute(]
        )
       " """
    )
    conn.executemany(]
       " "INSERT INTO enhanced_script_tracking VALUES(?,?,?,?,?")",
        []
            (str(base /" "a.p"y")," "utilitie"s"," "pytho"n", 80," "2021-01-0"1"),
            (str(base /" "b.s"h")," "script"s"," "bas"h", 60," "2021-01-0"2")])
    conn.commit()
    conn.close()


def test_organize_files_autonomously(tmp_path, monkeypatch):
    db = tmp_path /" "production.d"b"
    _setup_db(db, tmp_path)

    monkeypatch.setenv"("GH_COPILOT_WORKSPAC"E", str(tmp_path))
    mgr = AutonomousFileManager()
    result = mgr.organize_files_autonomously("["foo.p"y"," "bar.s"h"])

    assert result"["foo.p"y"] == str(tmp_path /" "utilitie"s" /" "foo.p"y")
    assert result"["bar.s"h"] == str(tmp_path /" "script"s" /" "bar.s"h")


def test_classify_file_autonomously(tmp_path, monkeypatch):
    db = tmp_path /" "production.d"b"
    _setup_db(db, tmp_path)

    monkeypatch.setenv"("GH_COPILOT_WORKSPAC"E", str(tmp_path))
    classifier = IntelligentFileClassifier()
    info = classifier.classify_file_autonomously"("foo.p"y")

    assert info"["categor"y"] ==" "utilitie"s"
    assert info"["typ"e"] ==" "pytho"n"
    assert info"["confidenc"e"] == 1.0


def test_create_intelligent_backup(tmp_path, monkeypatch):
    db = tmp_path /" "production.d"b"
    _setup_db(db, tmp_path)

    (tmp_path /" "a.p"y").write_text"("print"(''a'')")
    (tmp_path /" "b.s"h").write_text"("echo "b")

    monkeypatch.setenv"("GH_COPILOT_WORKSPAC"E", str(tmp_path))
    mgr = AutonomousBackupManager()
    backup_root = Path(tempfile.mkdtemp())
    monkeypatch.setattr(mgr," "backup_roo"t", backup_root)

    dest = mgr.create_intelligent_backup(file_priority"="LO"W")
    dest_path = Path(dest)

    assert (dest_path /" "a.p"y").is_file()
    assert (dest_path /" "b.s"h").is_file()
"