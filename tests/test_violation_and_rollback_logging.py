import sqlite3
from pathlib import Path

from dashboard import compliance_metrics_updater as cmu
from scripts.correction_logger_and_rollback import CorrectionLoggerRollback


def test_violation_and_rollback_logging(tmp_path, monkeypatch):
    events = []
    monkeypatch.setattr(cmu, "_log_event", lambda evt, **kw: events.append((kw.get("table"), evt)))
    monkeypatch.setattr(
        "scripts.correction_logger_and_rollback._log_event",
        lambda evt, **kw: events.append((kw.get("table"), evt)),
    )

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    analytics_db = db_dir / "analytics.db"
    with sqlite3.connect(analytics_db) as conn:
        conn.execute("CREATE TABLE todo_fixme_tracking (resolved INTEGER)")
        conn.execute("INSERT INTO todo_fixme_tracking VALUES (1)")
        conn.execute(
            "CREATE TABLE corrections (file_path TEXT, rationale TEXT, compliance_score REAL, rollback_reference TEXT, ts TEXT)"
        )
        conn.execute(
            "INSERT INTO corrections VALUES ('f','r',1.0,'b','ts')"
        )
        conn.execute("CREATE TABLE violation_logs (timestamp TEXT, details TEXT)")
        conn.execute(
            "CREATE TABLE rollback_logs (target TEXT, backup TEXT, timestamp TEXT)"
        )
        conn.commit()

    logger = CorrectionLoggerRollback(analytics_db)
    logger.log_violation("violation")

    target = tmp_path / "f.txt"
    target.write_text("x")
    logger.auto_rollback(target, None)

    dash = tmp_path / "dash"
    updater = cmu.ComplianceMetricsUpdater(dash)
    updater.update()

    assert any(t == "violation_logs" for t, _ in events)
    assert any(t == "rollback_logs" for t, _ in events)
