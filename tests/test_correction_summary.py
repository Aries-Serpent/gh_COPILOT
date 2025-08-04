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
            "CREATE TABLE corrections (file_path TEXT, rationale TEXT, correction_type TEXT, compliance_score REAL, score_delta REAL, rollback_reference TEXT, ts TEXT)"
        )
        conn.execute(
            "INSERT INTO corrections VALUES ('f.py','test','general',1.0,0.0,'', '2025-01-01')"
        )
    monkeypatch.setattr("scripts.correction_logger_and_rollback.DASHBOARD_DIR", tmp_path)
    monkeypatch.setattr(clr, "validate_enterprise_operation", lambda *a, **k: None)
    log = CorrectionLoggerRollback(analytics)
    summary = log.summarize_corrections(max_entries=1)
    assert summary["total_corrections"] == 1
    data = json.loads((tmp_path / "correction_summary.json").read_text())
    assert data["status"] == "complete"
    assert isinstance(data.get("corrections"), list)


def test_correction_summary_event_logged(tmp_path: Path, monkeypatch) -> None:
    analytics = tmp_path / "analytics.db"
    with sqlite3.connect(analytics) as conn:
        conn.execute(
            "CREATE TABLE corrections (file_path TEXT, rationale TEXT, correction_type TEXT, compliance_score REAL, score_delta REAL, rollback_reference TEXT, ts TEXT)"
        )
        conn.execute(
            "INSERT INTO corrections VALUES ('f.py','test','general',1.0,0.0,'', '2025-01-01')"
        )
    monkeypatch.setattr("scripts.correction_logger_and_rollback.DASHBOARD_DIR", tmp_path)
    monkeypatch.setattr(clr, "validate_enterprise_operation", lambda *a, **k: None)
    events = []
    monkeypatch.setattr(clr, "_log_event", lambda e, **_: events.append(e) or True)
    log = CorrectionLoggerRollback(analytics)
    log.summarize_corrections(max_entries=1)
    assert any(e.get("event") == "correction_summary" for e in events)
