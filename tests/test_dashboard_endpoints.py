#!/usr/bin/env python3
import sys
import types
import pytest

# Stub external dependencies not installed in the environment
sys.modules.setdefault("sklearn", types.ModuleType("sklearn"))
sys.modules.setdefault("sklearn.ensemble", types.SimpleNamespace(IsolationForest=None))
sys.modules.setdefault("sklearn.cluster", types.SimpleNamespace(KMeans=None))
sys.modules.setdefault("sklearn.datasets", types.SimpleNamespace(make_classification=None))
sys.modules.setdefault(
    "sklearn.model_selection", types.SimpleNamespace(train_test_split=None)
)
sys.modules.setdefault("sklearn.preprocessing", types.SimpleNamespace(StandardScaler=None))
sys.modules.setdefault("numpy", types.ModuleType("numpy"))
qiskit_stub = types.ModuleType("qiskit")
qiskit_stub.QuantumCircuit = None
sys.modules["qiskit"] = qiskit_stub
qcircuit = types.ModuleType("qiskit.circuit")
qcircuit.library = types.SimpleNamespace(QFT=None)
sys.modules["qiskit.circuit"] = qcircuit
sys.modules["qiskit.circuit.library"] = qcircuit.library
qinfo = types.ModuleType("qiskit.quantum_info")
qinfo.Statevector = None
sys.modules["qiskit.quantum_info"] = qinfo
qaer = types.ModuleType("qiskit_aer")
qaer.AerSimulator = None
sys.modules["qiskit_aer"] = qaer


class DummyCorrectionLoggerRollback:
    def __init__(self, *args, **kwargs):
        pass

    def auto_rollback(self, *args, **kwargs):
        return True


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
import web_gui.scripts.flask_apps.enterprise_dashboard as ed
from web_gui.scripts.flask_apps.enterprise_dashboard import app


@pytest.fixture(autouse=True)
def _stub_fetch_metrics(monkeypatch):
    monkeypatch.setattr(
        ed,
        "_fetch_metrics",
        lambda: {"metrics": {"composite_score": 0.0, "score_breakdown": {}}},
    )


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
    metrics = data.get("metrics", {})
    assert "composite_score" in metrics
    assert "score_breakdown" in metrics


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


def test_rollback_logs_endpoint():
    client = app.test_client()
    resp = client.get("/rollback_logs")
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_perform_rollback_endpoint():
    client = app.test_client()
    resp = client.post("/rollback", json={"target": "a.txt"})
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


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
