import sqlite3
from dashboard import compliance_metrics_updater as cmu


def test_scheduler_and_stream(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    analytics_db = db_dir / "analytics.db"
    with sqlite3.connect(analytics_db) as conn:
        conn.execute("CREATE TABLE todo_fixme_tracking (resolved INTEGER, status TEXT)")
        conn.execute("INSERT INTO todo_fixme_tracking VALUES (1, 'resolved')")
        conn.execute("CREATE TABLE correction_logs (compliance_score REAL)")
        conn.execute("INSERT INTO correction_logs VALUES (1.0)")
        conn.execute("CREATE TABLE violation_logs (timestamp TEXT, details TEXT)")
        conn.execute("CREATE TABLE rollback_logs (target TEXT, backup TEXT, timestamp TEXT)")

    monkeypatch.setattr(cmu, "ANALYTICS_DB", analytics_db)
    monkeypatch.setattr(cmu, "ensure_tables", lambda *a, **k: None)
    monkeypatch.setattr(cmu, "insert_event", lambda *a, **k: None)
    monkeypatch.setattr(cmu, "validate_no_recursive_folders", lambda: None)
    monkeypatch.setattr(cmu, "validate_environment_root", lambda: None)

    dash = tmp_path / "dashboard"
    updater = cmu.ComplianceMetricsUpdater(dash)
    gen = updater.stream_metrics(interval=0)
    metrics = next(gen)
    assert "suggestion" in metrics

    call_count = []
    monkeypatch.setattr(cmu.ComplianceMetricsUpdater, "update", lambda self, simulate=False: call_count.append(1))
    updater.run_scheduler(interval=0, iterations=3)
    assert len(call_count) == 3
