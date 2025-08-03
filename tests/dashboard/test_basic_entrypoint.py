import json
import sqlite3
from pathlib import Path

import pytest

from dashboard import enterprise_dashboard as ed


@pytest.fixture()
def app(tmp_path: Path, monkeypatch):
    metrics = tmp_path / "metrics.json"
    metrics.write_text(json.dumps({"metrics": {"placeholder_removal": 1}}))
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE rollback_logs(timestamp TEXT, target TEXT, backup TEXT)"
        )
        conn.execute(
            "INSERT INTO rollback_logs VALUES ('2024-01-01', 'file.py', 'file.bak')"
        )
    monkeypatch.setattr(ed, "METRICS_FILE", metrics)
    monkeypatch.setattr(ed, "ANALYTICS_DB", db)
    return ed.app


def test_metrics_endpoint(app):
    client = app.test_client()
    data = client.get("/metrics").get_json()
    assert data["metrics"]["placeholder_removal"] == 1


def test_rollback_logs_endpoint(app):
    client = app.test_client()
    data = client.get("/rollback-logs").get_json()
    assert data[0]["target"] == "file.py"


def test_html_views(app):
    client = app.test_client()
    assert client.get("/metrics/view").status_code == 200
    assert client.get("/rollback-logs/view").status_code == 200

