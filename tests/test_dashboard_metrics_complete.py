import json
import sqlite3
from pathlib import Path

from dashboard import compliance_metrics_updater as cmu


def test_dashboard_metrics_complete(tmp_path: Path, monkeypatch) -> None:
    analytics_db = tmp_path / "analytics.db"
    with sqlite3.connect(analytics_db) as conn:
        conn.execute("CREATE TABLE todo_fixme_tracking (resolved INTEGER, status TEXT)")
        conn.execute("INSERT INTO todo_fixme_tracking VALUES (1, 'resolved')")
        conn.execute("CREATE TABLE correction_logs (compliance_score REAL)")
        conn.execute("INSERT INTO correction_logs VALUES (1.0)")
        conn.execute("CREATE TABLE violation_logs (id INTEGER)")
    monkeypatch.setattr(cmu, "ANALYTICS_DB", analytics_db)
    monkeypatch.setattr(cmu, "validate_no_recursive_folders", lambda: None)
    monkeypatch.setattr(cmu, "validate_environment_root", lambda: None)
    monkeypatch.setattr(cmu, "ensure_tables", lambda *a, **k: None)
    monkeypatch.setattr(cmu, "insert_event", lambda *a, **k: None)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    dash = tmp_path / "dashboard"
    updater = cmu.ComplianceMetricsUpdater(dash, test_mode=True)
    monkeypatch.setattr(updater, "_check_forbidden_operations", lambda: None)
    updater.update()
    data = json.loads((dash / "metrics.json").read_text())
    assert data["status"] in {"issues_pending", "complete"}
    assert "compliance_score" in data["metrics"]
