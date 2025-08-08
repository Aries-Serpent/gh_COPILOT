"""Tests for correction log endpoint and Vue component pagination."""

import sqlite3
from pathlib import Path

from flask import Flask

from dashboard.routes import corrections as corrections_route


def _create_db(tmp_path: Path) -> Path:
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE correction_logs(timestamp TEXT, path TEXT, status TEXT)"
        )
        conn.execute(
            "INSERT INTO correction_logs VALUES ('2024-01-01', 'file.py', 'fixed')"
        )
    return db


def test_correction_logs_endpoint(tmp_path, monkeypatch):
    db = _create_db(tmp_path)
    monkeypatch.setattr(corrections_route, "ANALYTICS_DB", db)
    app = Flask(__name__)
    app.register_blueprint(corrections_route.bp)
    client = app.test_client()
    data = client.get("/corrections/logs").get_json()
    assert data[0]["path"] == "file.py"


def test_vue_component_has_pagination():
    content = Path("web/dashboard/components/CorrectionLog.vue").read_text()
    assert "nextPage" in content
    assert "pagedLogs" in content
