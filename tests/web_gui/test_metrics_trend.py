import os
import json
from pathlib import Path

from dashboard import enterprise_dashboard as gui

os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"


def test_metrics_trend(tmp_path, monkeypatch):
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    os.environ["GH_COPILOT_BACKUP_ROOT"] = str(tmp_path / "backup")
    (tmp_path / "backup").mkdir()
    metrics_file = tmp_path / "analytics" / "historical_metrics.json"
    metrics_file.parent.mkdir()
    metrics_file.write_text(json.dumps({"metrics": [1, 2, 3]}))

    monkeypatch.setattr(gui, "jsonify", lambda x: x)
    monkeypatch.setattr(gui, "HISTORICAL_METRICS_FILE", metrics_file)
    client = gui.app.test_client()
    data = client.get("/api/metrics/trend").get_json()
    assert data["metrics"] == [1.0, 2.0, 3.0]
    assert data["timestamps"] == [0, 1, 2]
