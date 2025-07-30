import json
import os
import sqlite3
from pathlib import Path

os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"
from scripts import correction_logger_and_rollback as clr
from scripts.correction_logger_and_rollback import CorrectionLoggerRollback


def test_correction_summary_generation(tmp_path: Path, monkeypatch) -> None:
    analytics = tmp_path / "analytics.db"
    with sqlite3.connect(analytics) as conn:
        conn.execute(
            (
                "CREATE TABLE correction_logs (file_path TEXT, compliance_score REAL, ts TEXT)"
            )
        )
        conn.execute("INSERT INTO correction_logs VALUES ('f.py',1.0,'2025-01-01')")
    monkeypatch.setattr("scripts.correction_logger_and_rollback.DASHBOARD_DIR", tmp_path)
    monkeypatch.setattr(clr, "validate_enterprise_operation", lambda *a, **k: None)
    log = CorrectionLoggerRollback(analytics)
    summary = log.summarize_corrections()
    assert summary["total_corrections"] == 1
    data = json.loads((tmp_path / "correction_summary.json").read_text())
    assert data["status"] == "complete"
