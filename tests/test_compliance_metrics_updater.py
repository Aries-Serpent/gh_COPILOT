import importlib
import json
import sqlite3
import pytest
import sys
import types


@pytest.mark.parametrize("simulate,test_mode", [(True, False), (False, True), (False, False)])
def test_compliance_metrics_updater(tmp_path, monkeypatch, simulate, test_mode):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    push_calls: list[dict] = []
    clr_calls: list[bool] = []

    class DummyCLR:
        def __init__(self, *a, **k):
            pass

        def summarize_corrections(self):
            clr_calls.append(True)

    stub = types.SimpleNamespace(
        CorrectionLoggerRollback=DummyCLR,
        validate_enterprise_operation=lambda *a, **k: None,
        _log_rollback=lambda *a, **k: None,
    )
    monkeypatch.setitem(sys.modules, "scripts.correction_logger_and_rollback", stub)
    module = importlib.import_module("dashboard.compliance_metrics_updater")
    importlib.reload(module)
    modes = []
    events = []
    monkeypatch.setattr(module, "ensure_tables", lambda *a, **k: None)
    monkeypatch.setattr(module, "push_metrics", lambda m, **k: push_calls.append(m))

    def _capture_event(event, table, **k):
        modes.append(k.get("test_mode"))
        events.append(table)

    monkeypatch.setattr(module, "insert_event", _capture_event)
    monkeypatch.setattr(module, "validate_no_recursive_folders", lambda: None)
    monkeypatch.setattr(module, "validate_environment_root", lambda: None)

    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    analytics_db = db_dir / "analytics.db"
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            "CREATE TABLE todo_fixme_tracking (resolved INTEGER, status TEXT, removal_id INTEGER)"
        )
        conn.execute("INSERT INTO todo_fixme_tracking VALUES (1, 'resolved', 1)")
        conn.execute("INSERT INTO todo_fixme_tracking VALUES (0, 'open', 2)")
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
    log_files = list(log_dir.glob("compliance_update_*.log"))
    assert log_files
    if not simulate:
        assert log_files[0].stat().st_size > 0

    assert "violation_logs" in events
    assert "rollback_logs" in events
    assert "correction_logs" in events

    metrics_file = dashboard_dir / "metrics.json"
    if simulate:
        assert not metrics_file.exists()
        return
    data = json.loads(metrics_file.read_text())
    assert data["metrics"]["placeholder_removal"] == 1
    expected_score = max(0.0, min(1.0, (1 / (1 + 1)) - 0.15))
    assert data["metrics"]["compliance_score"] == expected_score
    assert data["metrics"]["violation_count"] == 1
    assert data["metrics"]["rollback_count"] == 1
    assert data["metrics"]["progress_status"] == "issues_pending"
    assert 0.0 <= data["metrics"]["progress"] <= 1.0
    assert data["metrics"]["correction_count"] == 1
    expected = test_mode or simulate
    assert all((m == expected) or (m is None) for m in modes)
    assert called
    if simulate:
        assert not push_calls
        assert not clr_calls
    else:
        assert push_calls
        assert clr_calls


def test_correction_summary_ingestion(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    class DummyCLR:
        def __init__(self, *a, **k):
            pass

        def summarize_corrections(self):
            return {}

    stub = types.SimpleNamespace(
        CorrectionLoggerRollback=DummyCLR,
        validate_enterprise_operation=lambda *a, **k: None,
        _log_rollback=lambda *a, **k: None,
    )
    monkeypatch.setitem(sys.modules, "scripts.correction_logger_and_rollback", stub)
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
            "CREATE TABLE todo_fixme_tracking (resolved INTEGER, status TEXT, removal_id INTEGER)"
        )
        conn.execute("INSERT INTO todo_fixme_tracking VALUES (1, 'resolved', 1)")
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
