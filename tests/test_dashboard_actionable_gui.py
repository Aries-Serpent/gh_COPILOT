import json
import os

os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"
from dashboard import integrated_dashboard as gui


class DummyRollback:
    def __init__(self, db):
        pass

    def auto_rollback(self, target, backup=None):
        return True


def test_dashboard_endpoints(tmp_path, monkeypatch):
    metrics = tmp_path / "metrics.json"
    metrics.write_text(json.dumps({"metrics": {"issues": 5}}))
    comp_dir = tmp_path / "compliance"
    comp_dir.mkdir()
    comp_dir.joinpath("correction_summary.json").write_text(json.dumps({"corrections": []}))
    monkeypatch.setattr(gui, "METRICS_PATH", metrics)
    monkeypatch.setattr(gui, "CORRECTIONS_DIR", comp_dir)
    monkeypatch.setattr(gui, "ANALYTICS_DB", tmp_path / "analytics.db")
    monkeypatch.setattr(gui, "CorrectionLoggerRollback", DummyRollback)
    client = gui.app.test_client()
    assert client.get("/").status_code == 200
    assert client.get("/metrics").status_code == 200
    assert client.get("/corrections").status_code == 200
    assert client.get("/corrections/view").status_code == 200
    assert client.get("/compliance").status_code == 200
    resp = client.post("/rollback", json={"target": str(tmp_path / "file.txt")})
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"
