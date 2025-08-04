import sqlite3

from dashboard import compliance_metrics_updater as cmu
from scripts.correction_logger_and_rollback import CorrectionLoggerRollback


def test_violation_and_rollback_logging(tmp_path, monkeypatch):
    events = []
    monkeypatch.setattr(cmu, "insert_event", lambda evt, table, **kw: events.append((table, evt)))
    monkeypatch.setattr(
        "scripts.correction_logger_and_rollback._log_event",
        lambda evt, **kw: events.append((kw.get("table"), evt)),
    )
    rollback_calls = []
    monkeypatch.setattr(
        "scripts.correction_logger_and_rollback._log_rollback",
        lambda *a, **kw: rollback_calls.append(a),
    )

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    analytics_db = db_dir / "analytics.db"
    with sqlite3.connect(analytics_db) as conn:
        conn.execute("CREATE TABLE todo_fixme_tracking (resolved INTEGER, status TEXT, removal_id INTEGER)")
        conn.execute("INSERT INTO todo_fixme_tracking VALUES (1, 'resolved', 1)")
        conn.execute("CREATE TABLE correction_logs (file_path TEXT, compliance_score REAL, ts TEXT)")
        conn.execute("INSERT INTO correction_logs VALUES ('f',1.0,'ts')")
        conn.execute(
            "CREATE TABLE violation_logs (timestamp TEXT, event TEXT, details TEXT, cause TEXT, remediation_path TEXT, rollback_trigger TEXT, count INTEGER)"
        )
        conn.execute(
            "CREATE TABLE rollback_logs (target TEXT, backup TEXT, violation_id INTEGER, outcome TEXT, event TEXT, count INTEGER, timestamp TEXT)"
        )
        conn.commit()

    logger = CorrectionLoggerRollback(analytics_db)
    logger.log_violation("violation")

    target = tmp_path / "f.txt"
    target.write_text("x")
    logger.auto_rollback(target, None)

    dash = tmp_path / "dash"
    updater = cmu.ComplianceMetricsUpdater(dash, test_mode=True)
    monkeypatch.setattr(updater, "_check_forbidden_operations", lambda: None)
    updater.update()

    assert any(t == "violation_logs" for t, _ in events)
    assert any(t == "rollback_logs" for t, _ in events)
    assert len(rollback_calls) == 1
