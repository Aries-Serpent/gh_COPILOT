import sqlite3
from pathlib import Path

from flask import Flask

from src.dashboard.api import logs as logs_api


def create_db(tmp_path: Path) -> Path:
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE correction_logs(timestamp TEXT, path TEXT, status TEXT)"
        )
        conn.execute(
            "INSERT INTO correction_logs VALUES ('2024-01-01', 'file.py', 'fixed')"
        )
    return db


def test_correction_logs_api(tmp_path, monkeypatch):
    db = create_db(tmp_path)
    monkeypatch.setattr(logs_api, "ANALYTICS_DB", db)
    app = Flask(__name__)
    app.register_blueprint(logs_api.bp)
    client = app.test_client()
    data = client.get("/correction-logs").get_json()
    assert data[0]["path"] == "file.py"


def test_vue_component_exists():
    vue_path = Path("web/dashboard/components/CorrectionLog.vue")
    content = vue_path.read_text()
    assert "CorrectionLog" in content
    assert "log.timestamp" in content
