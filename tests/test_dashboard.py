import os
import sqlite3
import sys
import types
from pathlib import Path

import pytest


class DummyCorrectionLoggerRollback:
    def __init__(self, *args, **kwargs):
        pass


sys.modules.setdefault(
    "scripts.correction_logger_and_rollback",
    types.SimpleNamespace(CorrectionLoggerRollback=DummyCorrectionLoggerRollback),
)

os.environ.setdefault("GH_COPILOT_WORKSPACE", str(Path(__file__).resolve().parents[1]))

from dashboard import compliance_metrics_updater as cmu


def _stub_no_recursive_folders() -> None:
    return None


cmu.validate_no_recursive_folders = _stub_no_recursive_folders
from web_gui.scripts.flask_apps.enterprise_dashboard import app
from dashboard import enterprise_dashboard as ed


@pytest.fixture()
def temp_db(tmp_path: Path) -> Path:
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE rollback_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, target TEXT, backup TEXT, violation_id INTEGER, outcome TEXT, event TEXT, count INTEGER, timestamp TEXT)"
        )
        conn.execute("CREATE TABLE todo_fixme_tracking (resolved INTEGER, status TEXT)")
        conn.execute("CREATE TABLE correction_logs (compliance_score REAL)")
        conn.execute(
            "CREATE TABLE violation_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, event TEXT, details TEXT, cause TEXT, remediation_path TEXT, rollback_trigger TEXT, count INTEGER)"
        )
        conn.execute(
            "INSERT INTO rollback_logs (target, backup, outcome, event, timestamp) VALUES ('file.py', 'file.py.bak', 'success', 'rollback', '2024-01-01T00:00:00Z')"
        )
    return db


def test_fetch_compliance_metrics(tmp_path: Path, temp_db: Path, monkeypatch):
    monkeypatch.setattr(cmu, "ANALYTICS_DB", temp_db)
    
    def noop(*a: object, **k: object) -> None:
        return None

    monkeypatch.setattr(cmu, "ensure_tables", noop)
    monkeypatch.setattr(cmu, "validate_no_recursive_folders", _stub_no_recursive_folders)
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
    monkeypatch.setattr(cmu, "validate_no_recursive_folders", _stub_no_recursive_folders)
    monkeypatch.setattr(cmu, "validate_environment_root", noop)
    monkeypatch.setattr(cmu, "insert_event", noop)
    client = app.test_client()
    resp = client.get("/metrics_stream?once=1")
    assert resp.status_code == 200
    assert resp.data.startswith(b"data:")


def test_enterprise_dashboard_endpoints() -> None:
    client = ed.app.test_client()
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "metrics" in resp.get_json()

    resp = client.get("/rollback-logs")
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)

    resp = client.get("/dashboard/compliance")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "metrics" in data and "rollbacks" in data

    resp = client.get("/")
    assert resp.status_code == 200
    assert "Compliance Score" in resp.data.decode()

    resp = client.get("/metrics/view")
    assert resp.status_code == 200
    assert "Compliance Metrics" in resp.data.decode()

    resp = client.get("/rollback-logs/view")
    assert resp.status_code == 200
    assert "Rollback Logs" in resp.data.decode()
