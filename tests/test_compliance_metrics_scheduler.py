import sqlite3
import logging
import threading
import pytest
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
    metrics_list = list(updater.stream_metrics(interval=0, iterations=1))
    assert len(metrics_list) == 1
    assert "suggestion" in metrics_list[0]

    call_count = []
    monkeypatch.setattr(cmu.ComplianceMetricsUpdater, "update", lambda self, simulate=False: call_count.append(1))
    updater.run_scheduler(interval=0, iterations=3)
    assert len(call_count) == 3


def test_stream_metrics_violation(tmp_path, monkeypatch, caplog):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    analytics_db = db_dir / "analytics.db"
    with sqlite3.connect(analytics_db) as conn:
        conn.execute("CREATE TABLE todo_fixme_tracking (resolved INTEGER, status TEXT)")
        conn.execute("INSERT INTO todo_fixme_tracking VALUES (1, 'resolved')")
        conn.execute("CREATE TABLE correction_logs (compliance_score REAL)")
        conn.execute("INSERT INTO correction_logs VALUES (1.0)")

    monkeypatch.setattr(cmu, "ANALYTICS_DB", analytics_db)
    monkeypatch.setattr(cmu, "ensure_tables", lambda *a, **k: None)
    monkeypatch.setattr(cmu, "insert_event", lambda *a, **k: None)
    monkeypatch.setattr(cmu, "validate_no_recursive_folders", lambda: None)
    monkeypatch.setattr(cmu, "validate_environment_root", lambda: None)

    def _raise_violation(self) -> None:
        raise RuntimeError("Forbidden operation detected")

    monkeypatch.setattr(cmu.ComplianceMetricsUpdater, "_check_forbidden_operations", _raise_violation)

    dash = tmp_path / "dashboard"
    updater = cmu.ComplianceMetricsUpdater(dash)
    gen = updater.stream_metrics(interval=0)

    caplog.set_level(logging.ERROR)
    with pytest.raises(RuntimeError):
        next(gen)
    assert any("Forbidden operation detected" in rec.message for rec in caplog.records)


def test_stream_metrics_stop_event(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    analytics_db = db_dir / "analytics.db"
    with sqlite3.connect(analytics_db) as conn:
        conn.execute("CREATE TABLE todo_fixme_tracking (resolved INTEGER, status TEXT)")
        conn.execute("INSERT INTO todo_fixme_tracking VALUES (1, 'resolved')")
        conn.execute("CREATE TABLE correction_logs (compliance_score REAL)")
        conn.execute("INSERT INTO correction_logs VALUES (1.0)")

    monkeypatch.setattr(cmu, "ANALYTICS_DB", analytics_db)
    monkeypatch.setattr(cmu, "ensure_tables", lambda *a, **k: None)
    monkeypatch.setattr(cmu, "insert_event", lambda *a, **k: None)
    monkeypatch.setattr(cmu, "validate_no_recursive_folders", lambda: None)
    monkeypatch.setattr(cmu, "validate_environment_root", lambda: None)

    dash = tmp_path / "dashboard"
    updater = cmu.ComplianceMetricsUpdater(dash)
    stop = threading.Event()
    gen = updater.stream_metrics(interval=0, stop_event=stop)
    next(gen)
    stop.set()
    with pytest.raises(StopIteration):
        next(gen)
