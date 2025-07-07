import sqlite3
import tempfile
from pathlib import Path

from core.autonomous_file_manager import (
    AutonomousFileManager,
    IntelligentFileClassifier,
    AutonomousBackupManager,
)


def _setup_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    base = path.parent
    conn.execute(
        """
        CREATE TABLE enhanced_script_tracking(
            script_path TEXT,
            functionality_category TEXT,
            script_type TEXT,
            importance_score INTEGER,
            last_backup TEXT
        )
        """
    )
    conn.executemany(
        "INSERT INTO enhanced_script_tracking VALUES(?,?,?,?,?)",
        [
            (str(base / "a.py"), "utilities", "python", 80, "2021-01-01"),
            (str(base / "b.sh"), "scripts", "bash", 60, "2021-01-02"),
        ],
    )
    conn.commit()
    conn.close()


def test_organize_files_autonomously(tmp_path):
    db = tmp_path / "production.db"
    _setup_db(db)

    mgr = AutonomousFileManager(workspace_path=str(tmp_path))
    result = mgr.organize_files_autonomously(["foo.py", "bar.sh"])

    assert result["foo.py"] == str(tmp_path / "utilities" / "foo.py")
    assert result["bar.sh"] == str(tmp_path / "scripts" / "bar.sh")


def test_classify_file_autonomously(tmp_path):
    db = tmp_path / "production.db"
    _setup_db(db)

    classifier = IntelligentFileClassifier(workspace_path=str(tmp_path))
    info = classifier.classify_file_autonomously("foo.py")

    assert info["category"] == "utilities"
    assert info["type"] == "python"
    assert info["confidence"] == 1.0


def test_create_intelligent_backup(tmp_path, monkeypatch):
    db = tmp_path / "production.db"
    _setup_db(db)

    (tmp_path / "a.py").write_text("print('a')")
    (tmp_path / "b.sh").write_text("echo b")

    mgr = AutonomousBackupManager(workspace_path=str(tmp_path))
    backup_root = Path(tempfile.mkdtemp())
    monkeypatch.setattr(mgr, "backup_root", backup_root)

    dest = mgr.create_intelligent_backup(file_priority="LOW")
    dest_path = Path(dest)

    assert (dest_path / "a.py").is_file()
    assert (dest_path / "b.sh").is_file()

