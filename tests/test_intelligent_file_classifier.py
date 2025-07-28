import sqlite3
from pathlib import Path

from scripts.file_management.intelligent_file_classifier import IntelligentFileClassifier


def _setup_db(tmp_path: Path) -> Path:
    db = tmp_path / "production.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE enhanced_script_tracking(\n                script_id INTEGER PRIMARY KEY AUTOINCREMENT,\n                script_path TEXT,\n                script_content TEXT,\n                script_hash TEXT,\n                script_type TEXT,\n                functionality_category TEXT\n            )"
        )
        conn.execute(
            "CREATE TABLE script_tracking(id INTEGER PRIMARY KEY AUTOINCREMENT, file_path TEXT, file_hash TEXT, last_modified TEXT)"
        )
    return db


def test_classification_and_version(tmp_path: Path) -> None:
    db = _setup_db(tmp_path)
    with sqlite3.connect(db) as conn:
        conn.executemany(
            "INSERT INTO enhanced_script_tracking(script_path, script_hash, script_type, functionality_category) VALUES (?, ?, ?, ?)",
            [
                ("util1.py", "a", "python", "scripts"),
                ("util2.py", "b", "python", "scripts"),
            ],
        )

    file_path = tmp_path / "test.py"
    file_path.write_text("print('hi')")
    clf = IntelligentFileClassifier(db)

    result1 = clf.classify_file_autonomously(file_path)
    assert result1["category"] == "scripts"
    assert result1["type"] == "python"
    assert result1["confidence"] > 0
    assert result1["version"] == 1
    assert not result1["duplicate"]

    result2 = clf.classify_file_autonomously(file_path)
    assert result2["duplicate"]
    assert result2["version"] == 2
