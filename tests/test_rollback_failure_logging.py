import sqlite3
from scripts.correction_logger_and_rollback import CorrectionLoggerRollback


def test_rollback_failure_logged(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setenv("GH_COPILOT_TEST_MODE", "1")

    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    analytics_db = db_dir / "analytics.db"
    logger = CorrectionLoggerRollback(analytics_db)
    monkeypatch.setattr(logger, "_record_strategy_history", lambda *a, **k: None)
    monkeypatch.setenv("GH_COPILOT_TEST_MODE", "0")

    target = tmp_path / "missing.txt"
    assert not logger.auto_rollback(target, None)

    with sqlite3.connect(analytics_db) as conn:
        row = conn.execute("SELECT target FROM rollback_failures").fetchone()
    assert row[0] == str(target)
