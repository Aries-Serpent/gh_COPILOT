import os
import sqlite3
from pathlib import Path

from dashboard import enterprise_dashboard as gui

os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"


def _setup_db(db: Path) -> None:
    with sqlite3.connect(db) as conn:
        conn.execute(
            """
            CREATE TABLE code_quality_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lint_score REAL,
                test_score REAL,
                placeholder_score REAL,
                composite_score REAL,
                ts TEXT
            )
            """
        )
        conn.executemany(
            "INSERT INTO code_quality_metrics (lint_score, test_score, placeholder_score, composite_score, ts) VALUES (?, ?, ?, ?, ?)",
            [
                (1.0, 2.0, 3.0, 4.0, "2024-01-01T00:00:00"),
                (1.5, 2.5, 3.5, 4.5, "2024-01-02T00:00:00"),
            ],
        )
        conn.commit()


def test_code_quality_history(tmp_path, monkeypatch):
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    os.environ["GH_COPILOT_BACKUP_ROOT"] = str(tmp_path / "backup")
    (tmp_path / "backup").mkdir()
    db = tmp_path / "databases" / "analytics.db"
    db.parent.mkdir()
    _setup_db(db)

    monkeypatch.setattr(gui, "ANALYTICS_DB", db)
    monkeypatch.setattr(gui, "jsonify", lambda x: x)
    client = gui.app.test_client()
    data = client.get("/api/code_quality_history").get_json()
    assert data["timestamps"] == ["2024-01-01T00:00:00", "2024-01-02T00:00:00"]
    assert data["composite_score"] == [4.0, 4.5]
