import sqlite3
from pathlib import Path

import pytest

from dashboard import compliance_metrics_updater as cmu


@pytest.fixture()
def app(tmp_path: Path, monkeypatch):
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE todo_fixme_tracking (placeholder_type TEXT, status TEXT)"
        )
        conn.executemany(
            "INSERT INTO todo_fixme_tracking VALUES (?, 'open')",
            [("TODO",), ("FIXME",), ("TODO",)],
        )
        conn.execute(
            "CREATE TABLE correction_logs (event TEXT, score REAL, timestamp TEXT)"
        )
        conn.executemany(
            "INSERT INTO correction_logs VALUES ('update', ?, ?)",
            [(0.1, "2024-01-01"), (0.2, "2024-01-02")],
        )
        conn.execute(
            "CREATE TABLE violation_logs (details TEXT, timestamp TEXT)"
        )
        conn.execute(
            "CREATE TABLE rollback_logs (target TEXT, backup TEXT, timestamp TEXT)"
        )
    monkeypatch.setattr(cmu, "validate_no_recursive_folders", lambda: None)
    monkeypatch.setattr(cmu, "ensure_tables", lambda *a, **k: None)
    monkeypatch.setattr(cmu, "validate_environment_root", lambda: None)
    monkeypatch.setattr(cmu, "insert_event", lambda *a, **k: None)
    monkeypatch.setattr(cmu, "ANALYTICS_DB", db)
    from web_gui.scripts.flask_apps import enterprise_dashboard as ed

    monkeypatch.setattr(ed, "ANALYTICS_DB", db)
    monkeypatch.setattr(
        ed,
        "metrics_updater",
        cmu.ComplianceMetricsUpdater(tmp_path, test_mode=True),
    )
    return ed.app


def test_metrics_endpoint_includes_new_fields(app):
    client = app.test_client()
    data = client.get("/metrics").get_json()
    assert data["placeholder_breakdown"]["TODO"] == 2
    assert data["compliance_trend"] == [0.1, 0.2]


def test_dashboard_template_has_new_elements(app):
    client = app.test_client()
    html = client.get("/").data.decode()
    assert 'id="placeholder_breakdown"' in html
    assert 'id="compliance_trend"' in html

