import sqlite3
from pathlib import Path

import pytest

from dashboard import compliance_metrics_updater as cmu


def no_recursive_folders() -> None:
    return None


cmu.validate_no_recursive_folders = no_recursive_folders
from web_gui.scripts.flask_apps.enterprise_dashboard import app


@pytest.fixture()
def temp_db(tmp_path: Path) -> Path:
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE rollback_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, target TEXT, backup TEXT, timestamp TEXT)"
        )
        conn.execute("CREATE TABLE todo_fixme_tracking (resolved INTEGER, status TEXT)")
        conn.execute("CREATE TABLE correction_logs (compliance_score REAL)")
        conn.execute("CREATE TABLE violation_logs (id INTEGER)")
        conn.execute(
            "INSERT INTO rollback_logs (target, backup, timestamp) VALUES ('file.py', 'file.py.bak', '2024-01-01T00:00:00Z')"
        )
    return db


def test_fetch_compliance_metrics(tmp_path: Path, temp_db: Path, monkeypatch):
    monkeypatch.setattr(cmu, "ANALYTICS_DB", temp_db)
    
    def noop(*a: object, **k: object) -> None:
        return None

    monkeypatch.setattr(cmu, "ensure_tables", noop)
    monkeypatch.setattr(cmu, "validate_no_recursive_folders", no_recursive_folders)
    monkeypatch.setattr(cmu, "validate_environment_root", noop)
    updater = cmu.ComplianceMetricsUpdater(tmp_path, test_mode=True)
    metrics = updater._fetch_compliance_metrics(test_mode=True)
    assert metrics["rollback_count"] == 1
    assert metrics["recent_rollbacks"]


def test_metrics_stream(tmp_path: Path, temp_db: Path, monkeypatch):
    monkeypatch.setattr(cmu, "ANALYTICS_DB", temp_db)
    
    def noop(*a: object, **k: object) -> None:
        return None

    monkeypatch.setattr(cmu, "ensure_tables", noop)
    monkeypatch.setattr(cmu, "validate_no_recursive_folders", no_recursive_folders)
    monkeypatch.setattr(cmu, "validate_environment_root", noop)
    monkeypatch.setattr(cmu, "insert_event", noop)
    client = app.test_client()
    resp = client.get("/metrics_stream?once=1")
    assert resp.status_code == 200
    assert resp.data.startswith(b"data:")
