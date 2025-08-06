import importlib
import json
import sqlite3
import sys
import types


from enterprise_modules import compliance
import enterprise_modules.compliance as compliance_module


def test_violation_rollback_dashboard_output(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setattr(
        compliance_module, "validate_enterprise_operation", lambda *a, **k: True
    )

    db_path = tmp_path / "databases" / "analytics.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE violation_logs (timestamp TEXT, details TEXT)"
        )
        conn.execute(
            "INSERT INTO violation_logs (timestamp, details) VALUES ('ts', 'd')"
        )
        conn.execute(
            "CREATE TABLE rollback_logs (target TEXT, backup TEXT, timestamp TEXT)"
        )
        conn.execute(
            "INSERT INTO rollback_logs (target, backup, timestamp) VALUES ('t', 'b', 'ts')"
        )
        conn.execute(
            "CREATE TABLE todo_fixme_tracking (resolved INTEGER, status TEXT, removal_id INTEGER)"
        )
        conn.execute(
            "CREATE TABLE correction_logs (compliance_score REAL)"
        )
        conn.commit()

    push_calls = []

    class DummyEnterpriseUtility:
        def execute_utility(self):
            return True

    def dummy_push(*a, **k):
        push_calls.append(True)

    class DummyCorrectionLoggerRollback:
        def __init__(self, *a, **k):
            pass

        def log_violation(self, *a, **k):
            pass

        def log_change(self, *a, **k):
            pass

    stub_corr = types.SimpleNamespace(
        CorrectionLoggerRollback=DummyCorrectionLoggerRollback,
        validate_enterprise_operation=lambda *a, **k: None,
        _log_rollback=lambda *a, **k: None,
    )
    stub_monitor = types.SimpleNamespace(
        push_metrics=dummy_push,
        EnterpriseUtility=DummyEnterpriseUtility,
    )

    monkeypatch.setitem(sys.modules, "scripts.correction_logger_and_rollback", stub_corr)
    monkeypatch.setitem(sys.modules, "unified_monitoring_optimization_system", stub_monitor)

    module = importlib.import_module("dashboard.compliance_metrics_updater")
    importlib.reload(module)
    monkeypatch.setattr(module, "validate_no_recursive_folders", lambda: None)
    monkeypatch.setattr(module, "validate_environment_root", lambda: None)

    updater = module.ComplianceMetricsUpdater(tmp_path / "dashboard", test_mode=True)
    monkeypatch.setattr(updater, "_check_forbidden_operations", lambda: None)
    updater.update()

    metrics = json.loads((tmp_path / "dashboard" / "metrics.json").read_text())
    assert metrics["metrics"]["violation_count"] == 1
    assert metrics["metrics"]["rollback_count"] == 1
    assert push_calls

