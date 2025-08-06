import sqlite3
from pathlib import Path

from dashboard import compliance_metrics_updater as cmu


def test_violation_and_rollback_metrics(tmp_path: Path, monkeypatch) -> None:
    analytics_db = tmp_path / "analytics.db"
    with sqlite3.connect(analytics_db) as conn:
        conn.execute("CREATE TABLE todo_fixme_tracking (status TEXT)")
        conn.execute("INSERT INTO todo_fixme_tracking VALUES ('resolved')")
        conn.execute("CREATE TABLE correction_logs (compliance_score REAL)")
        conn.execute("INSERT INTO correction_logs VALUES (1.0)")
        conn.execute("CREATE TABLE violation_logs (event TEXT)")
        conn.execute("INSERT INTO violation_logs VALUES ('violation')")
        conn.execute(
            "CREATE TABLE rollback_logs (target TEXT, backup TEXT, timestamp TEXT)"
        )
        conn.execute(
            "INSERT INTO rollback_logs VALUES ('tgt', 'bkp', '2024-01-01T00:00:00')"
        )
    monkeypatch.setattr(cmu, "ANALYTICS_DB", analytics_db)
    monkeypatch.setattr(cmu, "validate_no_recursive_folders", lambda: None)
    monkeypatch.setattr(cmu, "validate_environment_root", lambda: None)
    monkeypatch.setattr(cmu, "ensure_tables", lambda *a, **k: None)
    monkeypatch.setattr(cmu, "insert_event", lambda *a, **k: None)

    class DummyCLR:
        def __init__(self, *a, **k):
            pass

        def log_violation(self, *a, **k):
            pass

        def log_change(self, *a, **k):
            pass

    monkeypatch.setattr(cmu, "CorrectionLoggerRollback", DummyCLR)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    updater = cmu.ComplianceMetricsUpdater(tmp_path, test_mode=True)
    monkeypatch.setattr(updater, "_check_forbidden_operations", lambda: None)
    metrics = updater._fetch_compliance_metrics(test_mode=True)
    assert metrics["violation_count"] == 1
    assert metrics["rollback_count"] == 1
    assert metrics["recent_rollbacks"] == [
        {"target": "tgt", "backup": "bkp", "timestamp": "2024-01-01T00:00:00"}
    ]
