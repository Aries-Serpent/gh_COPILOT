import sqlite3
from scripts.correction_logger_and_rollback import CorrectionLoggerRollback


def test_rollback_failure_logged(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setenv("GH_COPILOT_TEST_MODE", "1")

    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    analytics_db = db_dir / "analytics.db"
    with sqlite3.connect(analytics_db) as conn:
        conn.execute("CREATE TABLE event_log (event TEXT)")
        conn.commit()
    def _ensure(db_path):
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS rollback_logs (target TEXT, backup TEXT, timestamp TEXT)"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS rollback_failures (target TEXT, details TEXT, timestamp TEXT)"
            )
            conn.commit()
    monkeypatch.setattr("enterprise_modules.compliance.ensure_rollback_logs", _ensure)
    logger = CorrectionLoggerRollback(analytics_db)
    monkeypatch.setattr(logger, "_record_strategy_history", lambda *a, **k: None)
    monkeypatch.setenv("GH_COPILOT_TEST_MODE", "0")

    target = tmp_path / "missing.txt"
    assert not logger.auto_rollback(target, None)

    with sqlite3.connect(analytics_db) as conn:
        row = conn.execute("SELECT target FROM rollback_failures").fetchone()
        rlog = conn.execute("SELECT target FROM rollback_logs").fetchone()
    assert row[0] == str(target)
    assert rlog[0] == str(target)
