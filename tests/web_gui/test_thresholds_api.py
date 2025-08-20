import os
import json
from pathlib import Path

from dashboard import enterprise_dashboard as gui
from dashboard import integrated_dashboard

os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"


def test_thresholds_api(tmp_path, monkeypatch):
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    os.environ["GH_COPILOT_BACKUP_ROOT"] = str(tmp_path / "backup")
    (tmp_path / "backup").mkdir()
    tfile = tmp_path / "thresholds.json"
    thresholds = {"composite_score": {"warning": 90, "critical": 50}}
    tfile.write_text(json.dumps(thresholds))
    monkeypatch.setattr(integrated_dashboard, "THRESHOLDS_FILE", tfile)
    monkeypatch.setattr(gui, "jsonify", lambda x: x)
    client = gui.app.test_client()
    data = client.get("/api/thresholds").get_json()
    assert data == thresholds

