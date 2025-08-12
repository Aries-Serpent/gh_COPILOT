import importlib
import json
import logging
import sqlite3
import pytest
import sys
import types


@pytest.mark.parametrize("simulate,test_mode", [(True, False), (False, True), (False, False)])
def test_compliance_metrics_updater(tmp_path, monkeypatch, simulate, test_mode):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    push_calls = []
    executed = []

    class DummyEnterpriseUtility:
        def execute_utility(self):
            executed.append(True)
            return True

    def dummy_push(metrics, *, table="monitoring_metrics", db_path=None, session_id=None):
        push_calls.append((metrics, table, db_path, session_id))

    class DummyCorrectionLoggerRollback:
        instances = []

        def __init__(self, *a, **k):
            self.logged = {"violation": 0, "change": 0}
            DummyCorrectionLoggerRollback.instances.append(self)

        def log_violation(self, details: str) -> None:
            self.logged["violation"] += 1

        def log_change(self, *a, **k) -> None:
            self.logged["change"] += 1

    stub_corr = types.SimpleNamespace(
        CorrectionLoggerRollback=DummyCorrectionLoggerRollback,
        validate_enterprise_operation=lambda *a, **k: None,
        _log_rollback=lambda *a, **k: None,
    )
    stub_monitor = types.SimpleNamespace(
        push_metrics=dummy_push,
        EnterpriseUtility=DummyEnterpriseUtility,
    )
    stub_quantum = types.SimpleNamespace(quantum_score_stub=lambda x: 0.0)
    monkeypatch.setitem(sys.modules, "scripts.correction_logger_and_rollback", stub_corr)
    monkeypatch.setitem(sys.modules, "unified_monitoring_optimization_system", stub_monitor)
    monkeypatch.setitem(sys.modules, "quantum_algorithm_library_expansion", stub_quantum)
    logging.getLogger().handlers.clear()
    module = importlib.import_module("dashboard.compliance_metrics_updater")
    importlib.reload(module)
    modes = []
    events: list[tuple[str, dict]] = []
    monkeypatch.setattr(module, "ensure_tables", lambda *a, **k: None)
    monkeypatch.setattr(module, "push_metrics", lambda m, **k: push_calls.append(m))

    def _capture_event(event, table, **k):
        modes.append(k.get("test_mode"))
        events.append((table, event))

    monkeypatch.setattr(module, "insert_event", _capture_event)
    monkeypatch.setattr(module, "validate_no_recursive_folders", lambda: None)
    monkeypatch.setattr(module, "validate_environment_root", lambda: None)
    monkeypatch.setattr(module, "_run_ruff", lambda: 5)
    monkeypatch.setattr(module, "_run_pytest", lambda: (8, 2))

    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    analytics_db = db_dir / "analytics.db"
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            "CREATE TABLE todo_fixme_tracking (resolved INTEGER, status TEXT, removal_id INTEGER, placeholder_type TEXT)"
        )
        conn.execute(
            "INSERT INTO todo_fixme_tracking VALUES (1, 'resolved', 1, 'type1')"
        )
        conn.execute(
            "INSERT INTO todo_fixme_tracking VALUES (0, 'open', 2, 'type1')"
        )
        conn.execute(
            "CREATE TABLE placeholder_audit_snapshots (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp INTEGER, open_count INTEGER, resolved_count INTEGER)"
        )
        conn.execute(
            "INSERT INTO placeholder_audit_snapshots (timestamp, open_count, resolved_count) VALUES (1, 1, 0)"
        )
        conn.execute(
            "INSERT INTO placeholder_audit_snapshots (timestamp, open_count, resolved_count) VALUES (2, 1, 1)"
        )
        conn.execute("CREATE TABLE correction_logs (compliance_score REAL)")
        conn.execute("INSERT INTO correction_logs VALUES (0.9)")
        conn.execute("CREATE TABLE violation_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, details TEXT)")
        conn.execute("INSERT INTO violation_logs (timestamp, details) VALUES ('ts', 'd')")
        conn.execute(
            "CREATE TABLE rollback_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, target TEXT, backup TEXT, timestamp TEXT)"
        )
        conn.execute("INSERT INTO rollback_logs (target, backup, timestamp) VALUES ('t','b','ts')")

    called: list[bool] = []

    class DummyOrchestrator:
        def __init__(self, *a, **k):
            pass

        def run_backup_cycle(self):
            called.append(True)
            return tmp_path / "dummy"

    monkeypatch.setattr(module, "DisasterRecoveryOrchestrator", DummyOrchestrator)

    dashboard_dir = tmp_path / "dashboard"
    updater = module.ComplianceMetricsUpdater(dashboard_dir, test_mode=test_mode)
    updater.update(simulate=simulate)
    valid = updater.validate_update()
    if simulate:
        assert not valid
    else:
        assert valid

    log_dir = tmp_path / "logs" / "dashboard"
    log_files = sorted(log_dir.glob("compliance_update_*.log"))
    assert log_files

    assert any(
        t == "event_log" and e.get("description") == "violation_detected"
        for t, e in events
    )
    assert any(
        t == "event_log" and e.get("description") == "rollback_detected"
        for t, e in events
    )
    assert any(t == "correction_logs" for t, _ in events)

    metrics_file = dashboard_dir / "metrics.json"
    if simulate:
        assert not metrics_file.exists()
        assert not push_calls
        return
    data = json.loads(metrics_file.read_text())
    assert data["metrics"]["placeholder_removal"] == 1
    assert data["metrics"]["placeholder_trend"]
    lint_val = 100 if test_mode else 95
    test_val = 100 if test_mode else 80
    expected_score = 0.3 * lint_val + 0.4 * test_val + 0.2 * 50 + 0.1 * 100
    assert data["metrics"]["composite_score"] == expected_score
    assert data["metrics"]["compliance_score"] == pytest.approx(0.35)
    assert data["metrics"]["violation_count"] == 1
    assert data["metrics"]["rollback_count"] == 1
    assert data["metrics"]["progress_status"] == "issues_pending"
    assert 0.0 <= data["metrics"]["progress"] <= 1.0
    assert data["metrics"]["correction_count"] == 1
    expected = test_mode or simulate
    assert all((m == expected) or (m is None) for m in modes)
    expected_called = not (simulate or test_mode)
    assert bool(called) == expected_called
    assert push_calls
    keys = {k for call in push_calls for k in call}
    assert {"lint_score", "test_score", "placeholder_score"}.issubset(keys)
    if not test_mode:
        with sqlite3.connect(analytics_db) as conn:
            row = conn.execute(
                "SELECT ruff_issues, tests_passed, tests_failed, placeholders_open, placeholders_resolved, lint_score, test_score, placeholder_score, composite_score FROM code_quality_metrics ORDER BY id DESC LIMIT 1"
            ).fetchone()
        assert row == pytest.approx((5.0, 8.0, 2.0, 1.0, 1.0, float(lint_val), float(test_val), 50.0, expected_score), rel=1e-3)
    assert executed
    logger_instance = DummyCorrectionLoggerRollback.instances[0]
    assert logger_instance.logged["violation"] == 1
    assert logger_instance.logged["change"] == 1


def test_correction_summary_ingestion(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    class DummyCorrectionLoggerRollback:
        def __init__(self, *a, **k):
            pass

        def log_violation(self, *a, **k):
            pass

        def log_change(self, *a, **k):
            pass

    stub = types.SimpleNamespace(
        CorrectionLoggerRollback=DummyCorrectionLoggerRollback,
        validate_enterprise_operation=lambda *a, **k: None,
        _log_rollback=lambda *a, **k: None,
    )
    stub_monitor = types.SimpleNamespace(
        EnterpriseUtility=lambda: None,
        push_metrics=lambda *a, **k: None,
    )
    stub_quantum = types.SimpleNamespace(quantum_score_stub=lambda x: 0.0)
    monkeypatch.setitem(sys.modules, "scripts.correction_logger_and_rollback", stub)
    monkeypatch.setitem(sys.modules, "unified_monitoring_optimization_system", stub_monitor)
    monkeypatch.setitem(sys.modules, "quantum_algorithm_library_expansion", stub_quantum)
    logging.getLogger().handlers.clear()
    module = importlib.import_module("dashboard.compliance_metrics_updater")
    importlib.reload(module)
    monkeypatch.setattr(module, "ensure_tables", lambda *a, **k: None)
    monkeypatch.setattr(module, "insert_event", lambda *a, **k: None)
    monkeypatch.setattr(module, "validate_no_recursive_folders", lambda: None)
    monkeypatch.setattr(module, "validate_environment_root", lambda: None)

    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    analytics_db = db_dir / "analytics.db"
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            "CREATE TABLE todo_fixme_tracking (resolved INTEGER, status TEXT, removal_id INTEGER, placeholder_type TEXT)"
        )
        conn.execute(
            "INSERT INTO todo_fixme_tracking VALUES (1, 'resolved', 1, 'type1')"
        )
        conn.execute("CREATE TABLE correction_logs (event TEXT, compliance_score REAL)")
        conn.execute("INSERT INTO correction_logs VALUES ('update', 0.9)")
        conn.execute("CREATE TABLE violation_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, details TEXT)")

    corr_dir = tmp_path / "dashboard" / "compliance"
    corr_dir.mkdir(parents=True)
    summary = {
        "timestamp": "ts",
        "total_corrections": 1,
        "corrections": [
            {
                "file_path": "file.py",
                "rationale": "fix",
                "compliance_score": 0.9,
                "rollback_reference": "ref",
                "timestamp": "ts",
                "root_cause": "coding standards",
            }
        ],
        "status": "complete",
    }
    (corr_dir / "correction_summary.json").write_text(json.dumps(summary))

    updater = module.ComplianceMetricsUpdater(tmp_path / "dashboard", test_mode=True)
    updater.update(simulate=False)
    data = json.loads((tmp_path / "dashboard" / "metrics.json").read_text())
    assert data["metrics"]["correction_logs"][0]["file_path"] == "file.py"
