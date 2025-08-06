import json
import sqlite3
from pathlib import Path

import pytest

from web_gui import dashboard_actionable_gui as gui


@pytest.fixture()
def gui_app(tmp_path: Path, monkeypatch):
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE placeholder_audit(id INTEGER)")
        conn.execute("INSERT INTO placeholder_audit VALUES (1)")
        conn.execute("CREATE TABLE rollback_logs(timestamp TEXT, details TEXT)")
        conn.execute("INSERT INTO rollback_logs VALUES ('2024-01-01', 'rolled')")
        conn.execute("CREATE TABLE violation_logs(timestamp TEXT, details TEXT)")
        conn.execute("INSERT INTO violation_logs VALUES ('2024-01-02', 'violation')")
    metrics = tmp_path / "metrics.json"
    metrics.write_text(json.dumps({"placeholder_removal": 0}))
    comp_dir = tmp_path / "compliance"
    comp_dir.mkdir()
    comp_dir.joinpath("correction_summary.json").write_text(
        json.dumps({"corrections": [{"file": "file.py"}]})
    )
    monkeypatch.setattr(gui, "METRICS_PATH", metrics)
    monkeypatch.setattr(gui, "CORRECTIONS_DIR", comp_dir)
    monkeypatch.setattr(gui, "ANALYTICS_DB", db)
    return gui.app


def test_metrics_reflect_database(gui_app):
    client = gui_app.test_client()
    data = client.get("/metrics").get_json()
    assert data["violation_count"] == 1
    assert data["rollback_count"] == 1


def test_corrections_endpoint(gui_app):
    client = gui_app.test_client()
    data = client.get("/corrections").get_json()
    assert data["corrections"][0]["file"] == "file.py"


def test_compliance_endpoint(gui_app):
    client = gui_app.test_client()
    data = client.get("/compliance").get_json()
    assert data["metrics"]["violation_count"] == 1
    assert data["corrections"][0]["file"] == "file.py"


def test_violations_endpoint_no_recursion_warning(gui_app, caplog):
    client = gui_app.test_client()
    with caplog.at_level("WARNING"):
        data = client.get("/violations").get_json()
    assert data["violations"][0]["details"] == "violation"
    assert "recurs" not in caplog.text.lower()
