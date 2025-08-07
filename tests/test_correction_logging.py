import sqlite3

import dashboard.enterprise_dashboard as ed
from scripts.correction_logger_and_rollback import CorrectionLoggerRollback
from enterprise_modules import compliance
from utils.cross_platform_paths import CrossPlatformPathManager


def test_correction_logged_and_dashboard(monkeypatch, tmp_path):
    monkeypatch.setattr(compliance, "validate_enterprise_operation", lambda *_: True)
    monkeypatch.setattr(CrossPlatformPathManager, "get_workspace_path", lambda: tmp_path)
    db = tmp_path / "analytics.db"
    logger = CorrectionLoggerRollback(db)
    target = tmp_path / "file.txt"
    logger.log_change(target, "rationale", compliance_score=0.8)
    with sqlite3.connect(db) as conn:
        row = conn.execute(
            "SELECT path, compliance_score, status, timestamp FROM correction_logs"
        ).fetchone()
    assert row[0].endswith("file.txt")
    assert row[1] == 0.8
    assert row[2] == "logged"
    assert row[3]
    monkeypatch.setattr(ed, "ANALYTICS_DB", db)
    monkeypatch.setattr(ed, "_load_metrics", lambda: {})
    monkeypatch.setattr(ed, "get_rollback_logs", lambda: [])
    monkeypatch.setattr(ed, "_load_sync_events", lambda: [])
    monkeypatch.setattr(ed, "_load_audit_results", lambda: [])
    client = ed.app.test_client()
    data = client.get("/corrections").get_json()
    assert data[0]["status"] == "logged"
    page = client.get("/").get_data(as_text=True)
    assert "Recent Corrections" in page
    assert "file.txt" in page
