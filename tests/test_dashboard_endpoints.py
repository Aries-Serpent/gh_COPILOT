#!/usr/bin/env python3
import sys
import types


class DummyCorrectionLoggerRollback:
    def __init__(self, *args, **kwargs):
        pass


sys.modules.setdefault(
    "scripts.correction_logger_and_rollback",
    types.SimpleNamespace(CorrectionLoggerRollback=DummyCorrectionLoggerRollback),
)
from dashboard import compliance_metrics_updater as cmu


def _stub_no_recursive_folders() -> None:
    return None


def _stub_no_environment_root() -> None:
    return None


cmu.validate_no_recursive_folders = _stub_no_recursive_folders
cmu.validate_environment_root = _stub_no_environment_root
from web_gui.scripts.flask_apps.enterprise_dashboard import app


def test_index_endpoint():
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.data.decode()
    assert "<h1>Compliance Dashboard</h1>" in data
    assert "metrics_stream" in data


def test_metrics_endpoint():
    client = app.test_client()
    resp = client.get("/metrics")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, dict)


def test_compliance_endpoint():
    client = app.test_client()
    resp = client.get("/compliance")
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), dict)


def test_dashboard_compliance_endpoint():
    client = app.test_client()
    resp = client.get("/dashboard/compliance")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "metrics" in data
    assert "rollbacks" in data


def test_rollback_alerts_endpoint():
    client = app.test_client()
    resp = client.get("/rollback_alerts")
    assert resp.status_code == 200


def test_rollback_history_endpoint():
    client = app.test_client()
    resp = client.get("/rollback_history")
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_dashboard_info_endpoint():
    client = app.test_client()
    resp = client.get("/dashboard_info")
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), dict)


def test_summary_endpoint():
    client = app.test_client()
    resp = client.get("/summary")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "metrics" in data
    assert "alerts" in data


def test_health_endpoint():
    client = app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_error_endpoint():
    client = app.test_client()
    resp = client.get("/error")
    assert resp.status_code == 500
    data = resp.get_json()
    assert data["status"] == "error"


def test_violations_endpoint():
    client = app.test_client()
    resp = client.get("/violations")
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_reports_endpoint():
    client = app.test_client()
    resp = client.get("/reports")
    assert resp.status_code == 200


def test_realtime_metrics_endpoint():
    client = app.test_client()
    resp = client.get("/realtime_metrics")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "metrics" in data
    assert "corrections" in data


def test_correction_history_endpoint():
    client = app.test_client()
    resp = client.get("/correction_history")
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)
