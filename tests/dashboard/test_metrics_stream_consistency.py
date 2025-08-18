import json
import sqlite3
import time
from pathlib import Path

from flask import Flask

import dashboard.enterprise_dashboard as ed
from web_gui.scripts.flask_apps.template_intelligence_engine import (
    TemplateIntelligenceEngine,
)
import pytest


@pytest.fixture(scope="session", autouse=True)
def apply_repo_migrations():
    """Override repo-level migrations to avoid altering test DB."""
    yield


def _setup_db(tmp_path: Path) -> None:
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE compliance_metrics_history (ts INTEGER, composite_score REAL, lint_score REAL, test_score REAL, placeholder_score REAL)"
        )
        conn.execute(
            "INSERT INTO compliance_metrics_history VALUES (?,?,?,?,?)",
            (int(time.time()), 90.0, 80.0, 85.0, 95.0),
        )
        conn.commit()
    ed.ANALYTICS_DB = db


def test_metrics_stream_matches_api(tmp_path):
    _setup_db(tmp_path)
    client = ed.app.test_client()
    api_resp = client.get("/api/compliance_scores")
    expected = api_resp.get_json()["scores"]

    stream_resp = client.get("/metrics_stream?once=1")
    payload = json.loads(stream_resp.data.decode().split("\n\n")[0].replace("data: ", ""))
    assert payload["compliance_scores"] == expected


def test_dashboard_template_enhancements(tmp_path):
    template_dir = Path(__file__).resolve().parents[2] / "web_gui" / "templates"
    app = Flask(__name__, template_folder=str(template_dir))
    engine = TemplateIntelligenceEngine(template_dir)
    metrics = {
        "placeholder_removal": 1,
        "compliance_score": 1.0,
        "violation_count": 0,
        "rollback_count": 0,
    }
    with app.test_request_context():
        html = engine.render_intelligent_template(
            "dashboard.html", {"metrics": metrics, "title": "Dashboard"}
        )
    assert "id=\"complianceChart\"" in html
    assert "title=\"Number of placeholders removed" in html
