import json
from pathlib import Path

from dashboard import integrated_dashboard as gui


def test_alert_levels_from_thresholds(tmp_path, monkeypatch):
    thresholds = {"lint_score": {"warning": 80, "critical": 50}}
    tfile = tmp_path / "thresholds.json"
    tfile.write_text(json.dumps(thresholds))
    monkeypatch.setattr(gui, "THRESHOLDS_FILE", tfile)
    mfile = tmp_path / "metrics.json"
    mfile.write_text(json.dumps({"metrics": {"lint_score": 40}}))
    monkeypatch.setattr(gui, "METRICS_FILE", mfile)
    monkeypatch.setattr(gui, "ANALYTICS_DB", tmp_path / "analytics.db")
    client = gui.app.test_client()
    data = client.get("/metrics").get_json()["metrics"]
    assert data["alerts"]["lint_score"] == "critical"
    assert data["thresholds"]["lint_score"] == thresholds["lint_score"]
