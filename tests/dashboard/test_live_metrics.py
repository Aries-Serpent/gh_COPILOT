import json
import sqlite3
from pathlib import Path
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from web_gui.scripts.flask_apps import enterprise_dashboard as ed


@pytest.fixture()
def test_app(tmp_path: Path, monkeypatch):
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE todo_fixme_tracking (resolved INTEGER, status TEXT)")
        conn.execute("INSERT INTO todo_fixme_tracking VALUES (1, 'ok')")
        conn.execute("INSERT INTO todo_fixme_tracking VALUES (0, 'open')")
        conn.execute("CREATE TABLE correction_logs (compliance_score REAL, ts TEXT)")
        conn.execute("INSERT INTO correction_logs VALUES (0.9, '2024-01-01T00:00:00Z')")
        conn.execute("CREATE TABLE violation_logs (details TEXT, timestamp TEXT)")
        conn.execute("INSERT INTO violation_logs VALUES ('violation', '2024-01-01T00:00:00Z')")
        conn.execute("CREATE TABLE rollback_logs (target TEXT, backup TEXT, timestamp TEXT)")
        conn.execute("INSERT INTO rollback_logs VALUES ('file.py', 'file.bak', '2024-01-01T00:00:00Z')")
    monkeypatch.setattr(ed, "ANALYTICS_DB", db)
    return ed.app


def test_metrics_stream_once(test_app):
    client = test_app.test_client()
    resp = client.get("/metrics_stream?once=1")
    assert resp.status_code == 200
    line = resp.data.decode().split("\n")[0]
    assert line.startswith("data:")
    metrics = json.loads(line.split("data: ")[1])
    assert metrics["placeholder_removal"] == 1


def test_alerts_endpoint(test_app):
    client = test_app.test_client()
    resp = client.get("/alerts")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["violations"]) == 1
    assert len(data["rollbacks"]) == 1
