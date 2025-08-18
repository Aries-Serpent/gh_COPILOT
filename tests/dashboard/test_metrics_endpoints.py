import json
import sqlite3
import time

import pytest

@pytest.fixture(scope="session", autouse=True)
def apply_repo_migrations():
    """Override repo-level migrations to avoid altering test DB."""
    yield

@pytest.fixture
def client(tmp_path):
    import dashboard.enterprise_dashboard as ed

    db = tmp_path / "analytics.db"
    conn = sqlite3.connect(db)
    conn.execute(
        "CREATE TABLE compliance_metrics_history (ts INTEGER, composite_score REAL)"
    )
    conn.execute(
        "INSERT INTO compliance_metrics_history (ts, composite_score) VALUES (?, ?)",
        (int(time.time()), 88.5),
    )
    conn.execute(
        "CREATE TABLE monitoring_metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp INTEGER, metrics_json TEXT)"
    )
    conn.execute(
        "INSERT INTO monitoring_metrics (timestamp, metrics_json) VALUES (?, ?)",
        (int(time.time()), json.dumps({"health_score": 91.0})),
    )
    conn.execute(
        "CREATE TABLE sync_events_log (event_time INTEGER, event_type TEXT, details TEXT)"
    )
    now = int(time.time())
    conn.executemany(
        "INSERT INTO sync_events_log (event_time, event_type, details) VALUES (?, ?, ?)",
        [(now - 5, "success", ""), (now - 2, "failure", "")],
    )
    conn.commit()
    conn.close()

    ed.ANALYTICS_DB = db
    return ed.app.test_client()


def test_metrics_compliance_endpoint(client):
    resp = client.get("/metrics/compliance")
    data = resp.get_json()
    assert data["metrics"]["value"] > 0


def test_metrics_monitoring_endpoint(client):
    resp = client.get("/metrics/monitoring")
    data = resp.get_json()
    assert data["metrics"]["value"] > 0


def test_metrics_synchronization_endpoint(client):
    resp = client.get("/metrics/synchronization")
    data = resp.get_json()
    assert data["metrics"]["value"] > 0
