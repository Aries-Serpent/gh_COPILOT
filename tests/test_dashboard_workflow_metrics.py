"""Tests for codex_dashboard_workflow database metrics helper."""

from __future__ import annotations

import sqlite3
from flask import Flask, jsonify

from codex_dashboard_workflow import fetch_panel_metrics


def test_metrics_endpoint_returns_database_values(tmp_path, monkeypatch):
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE dashboard_metrics (panel TEXT PRIMARY KEY, value REAL, target REAL, unit TEXT)"
        )
        conn.execute(
            "INSERT INTO dashboard_metrics VALUES ('compliance', 75.0, 100.0, '%')"
        )

    # point helper to temporary database
    monkeypatch.setattr("codex_dashboard_workflow.ANALYTICS_DB", db)

    app = Flask(__name__)

    @app.route("/metrics/compliance")
    def metrics_compliance():
        metrics = fetch_panel_metrics("compliance")
        return jsonify({"metrics": metrics})

    client = app.test_client()
    resp = client.get("/metrics/compliance")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["metrics"] == {"value": 75.0, "target": 100.0, "unit": "%"}
