import sqlite3
from scripts.correction_logger_and_rollback import CorrectionLoggerRollback


def test_strategy_adapts_with_history(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    events = []
    monkeypatch.setattr(
        "scripts.correction_logger_and_rollback._log_event",
        lambda evt, **kw: events.append((kw.get("table"), evt)),
    )

    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    db = db_dir / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE event_log (event TEXT)")
        conn.commit()
    def _ensure(db_path):
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS rollback_logs (target TEXT, backup TEXT, timestamp TEXT)"
            )
            conn.commit()
    monkeypatch.setattr("enterprise_modules.compliance.ensure_rollback_logs", _ensure)
    logger = CorrectionLoggerRollback(db)

    target = tmp_path / "file.txt"
    backup = tmp_path / "file.bak"
    target.write_text("a")
    backup.write_text("a")

    # first rollback
    assert logger.auto_rollback(target, backup)
    with sqlite3.connect(db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM rollback_logs").fetchone()[0]
    assert count >= 1
    assert logger.suggest_rollback_strategy(target) == "Standard rollback"

    # second rollback
    target.write_text("b")
    assert logger.auto_rollback(target, backup)
    with sqlite3.connect(db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM rollback_logs").fetchone()[0]
    assert count >= 2
    assert logger.suggest_rollback_strategy(target) == "Automate regression tests for this file."

    # induce failures
    target.unlink()
    logger.auto_rollback(target, None)
    logger.auto_rollback(target, None)
    msg = logger.suggest_rollback_strategy(target)
    assert "audit" in msg.lower()

    with sqlite3.connect(db) as conn:
        failure_entries = conn.execute("SELECT COUNT(*) FROM rollback_logs").fetchone()[0]
    assert failure_entries >= 4

    assert any(t == "rollback_strategy_history" for t, _ in events)
