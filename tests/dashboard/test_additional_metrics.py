from pathlib import Path

import sqlite3
import pytest

from dashboard import compliance_metrics_updater as cmu


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
        conn.execute("CREATE TABLE rollback_logs (target TEXT, backup TEXT, timestamp TEXT)")
        conn.execute(
            """
            CREATE TABLE integration_score_calculations (
                calculation_id TEXT PRIMARY KEY,
                timestamp TEXT,
                overall_score REAL,
                maximum_possible_score REAL,
                percentage_score REAL,
                achievement_level TEXT,
                integration_status TEXT,
                calculation_passed BOOLEAN,
                critical_disqualifiers TEXT,
                component_scores TEXT,
                recommendations TEXT
            )
            """
        )
        conn.execute(
            """
            INSERT INTO integration_score_calculations (
                calculation_id, timestamp, overall_score, maximum_possible_score,
                percentage_score, achievement_level, integration_status,
                calculation_passed, critical_disqualifiers, component_scores, recommendations
            ) VALUES ('1', '2024-01-01T00:00:00Z', 0, 0, 0, '', 'FULLY_INTEGRATED', 1, '[]', '{}', '[]')
            """
        )
        conn.execute(
            """
            CREATE TABLE performance_metrics (
                id INTEGER PRIMARY KEY,
                metric_name TEXT,
                metric_value REAL,
                metric_type TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            "INSERT INTO performance_metrics (metric_name, metric_value, metric_type) VALUES ('query_latency', 12.5, 'ms')"
        )
    monkeypatch.setattr(cmu, "validate_no_recursive_folders", lambda: None)
    monkeypatch.setattr(cmu, "ensure_tables", lambda *a, **k: None)
    monkeypatch.setattr(cmu, "validate_environment_root", lambda: None)
    monkeypatch.setattr(cmu, "insert_event", lambda *a, **k: None)
    import importlib
    from web_gui.scripts.flask_apps import enterprise_dashboard as ed
    ed = importlib.reload(ed)

    monkeypatch.setattr(ed, "ANALYTICS_DB", db)
    monkeypatch.setattr(
        ed,
        "metrics_updater",
        cmu.ComplianceMetricsUpdater(tmp_path, test_mode=True),
    )
    return ed.app


def test_additional_metrics_present(test_app):
    client = test_app.test_client()
    resp = client.get("/summary")
    assert resp.status_code == 200
    metrics = resp.get_json()["metrics"]
    assert metrics["lessons_integration_status"] == "FULLY_INTEGRATED"
    assert metrics["average_query_latency"] == pytest.approx(12.5)
    assert metrics["compliance_score"] == 0.0


def test_metrics_endpoint_additional_metrics(test_app):
    client = test_app.test_client()
    resp = client.get("/metrics")
    assert resp.status_code == 200
    metrics = resp.get_json()
    assert metrics["lessons_integration_status"] == "FULLY_INTEGRATED"
    assert metrics["average_query_latency"] == pytest.approx(12.5)
    assert metrics["compliance_score"] == 0.0

