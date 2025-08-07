import os
import sqlite3
from pathlib import Path

import pytest

from dashboard import integrated_dashboard as gui


os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"


def _setup_db(db: Path) -> None:
    with sqlite3.connect(db) as conn:
        conn.execute(
            """
            CREATE TABLE code_quality_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ruff_issues INTEGER,
                tests_passed INTEGER,
                tests_failed INTEGER,
                placeholders INTEGER,
                composite_score REAL,
                ts TEXT
            )
            """
        )
        conn.execute(
            "INSERT INTO code_quality_metrics (ruff_issues, tests_passed, tests_failed, placeholders, composite_score, ts) VALUES (?, ?, ?, ?, ?, ?)",
            (1, 5, 0, 0, 0.0, "2024-01-01T00:00:00"),
        )
        conn.commit()


def test_metrics_change_after_audit_and_rollback(tmp_path, monkeypatch):
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    os.environ["GH_COPILOT_BACKUP_ROOT"] = str(tmp_path / "backup")
    (tmp_path / "backup").mkdir()
    db = tmp_path / "databases" / "analytics.db"
    db.parent.mkdir()
    _setup_db(db)

    monkeypatch.setattr(gui, "ANALYTICS_DB", db)
    monkeypatch.setattr(gui, "METRICS_PATH", tmp_path / "metrics.json")
    monkeypatch.setattr(gui, "CORRECTIONS_DIR", tmp_path)

    client = gui.app.test_client()

    data = client.get("/metrics").get_json()
    assert data["violation_count"] == 0
    assert data["rollback_count"] == 0
    assert data["compliance_score"] == pytest.approx(99.6, rel=1e-3)

    logger = gui.CorrectionLoggerRollback(db)
    logger.log_change(tmp_path / "file.py", "placeholder fix", correction_type="placeholder")

    assert client.get("/metrics").get_json()["violation_count"] > 0

    target = tmp_path / "target.txt"
    backup = tmp_path / "backup.txt"
    backup.write_text("original")
    target.write_text("modified")
    logger.auto_rollback(target, backup)

    assert client.get("/metrics").get_json()["rollback_count"] > 0
