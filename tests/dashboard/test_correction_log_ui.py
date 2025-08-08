"""Tests for corrections API and Vue component."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from flask import Flask

from src.dashboard.api import corrections as corrections_api


def _setup_db(tmp_path: Path) -> Path:
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE sync_events_log (source TEXT, target TEXT, ts TEXT)"
        )
        conn.execute(
            "INSERT INTO sync_events_log VALUES ('entity-a', 'resolved', '2024-01-01')"
        )
    return db


def test_corrections_api(tmp_path, monkeypatch):
    db = _setup_db(tmp_path)
    monkeypatch.setattr(corrections_api, "ANALYTICS_DB", db)
    app = Flask(__name__)
    app.register_blueprint(corrections_api.bp)
    client = app.test_client()
    data = client.get("/api/corrections").get_json()
    assert data[0]["entity"] == "entity-a"
    assert data[0]["resolution"] == "resolved"


def test_vue_component_includes_fields():
    vue_path = Path("web/dashboard/components/CorrectionLog.vue")
    content = vue_path.read_text()
    assert "log.entity" in content
    assert "log.resolution" in content

