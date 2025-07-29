import importlib
from pathlib import Path

from dashboard import compliance_metrics_updater as cmu


def test_dashboard_update_logs_event(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    events = []
    monkeypatch.setattr(cmu, "_log_event", lambda evt, **_: events.append(evt))
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    (db_dir / "analytics.db").touch()
    dash = tmp_path / "dashboard"
    updater = cmu.ComplianceMetricsUpdater(dash)
    updater._fetch_compliance_metrics = lambda: {}
    updater.update()
    assert any(e.get("event") == "dashboard_update" for e in events)
