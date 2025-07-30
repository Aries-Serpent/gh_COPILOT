import importlib
import json
import sqlite3


def test_compliance_metrics_updater(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    module = importlib.import_module("dashboard.compliance_metrics_updater")
    importlib.reload(module)
    events = []
    monkeypatch.setattr(module, "ensure_tables", lambda *a, **k: None)
    monkeypatch.setattr(module, "insert_event", lambda e, table, **k: events.append(table))
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
        conn.execute("CREATE TABLE correction_logs (compliance_score REAL)")
        conn.execute("INSERT INTO correction_logs VALUES (0.9)")
        conn.execute(
            "CREATE TABLE violation_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, details TEXT)"
        )
        conn.execute(
            "INSERT INTO violation_logs (timestamp, details) VALUES ('ts', 'd')"
        )
        conn.execute(
            "CREATE TABLE rollback_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, target TEXT, backup TEXT, timestamp TEXT)"
        )
        conn.execute(
            "INSERT INTO rollback_logs (target, backup, timestamp) VALUES ('t','b','ts')"
        )

    dashboard_dir = tmp_path / "dashboard"
    updater = module.ComplianceMetricsUpdater(dashboard_dir)
    updater.update()
    assert updater.validate_update()

    assert "violation_logs" in events
    assert "rollback_logs" in events
    assert "correction_logs" in events

    metrics_file = dashboard_dir / "metrics.json"
    assert metrics_file.exists()
    data = json.loads(metrics_file.read_text())
    assert data["metrics"]["placeholder_removal"] == 1
    assert data["metrics"]["compliance_score"] == 0.9
    assert data["metrics"]["violation_count"] == 1
    assert data["metrics"]["rollback_count"] == 1
    assert data["metrics"]["progress_status"] == "issues_pending"
    assert 0.0 <= data["metrics"]["progress"] <= 1.0
    assert data["metrics"]["correction_count"] == 1
