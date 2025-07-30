from scripts.correction_logger_and_rollback import CorrectionLoggerRollback


def test_strategy_adapts_with_history(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    events = []
    monkeypatch.setattr(
        "scripts.correction_logger_and_rollback._log_event",
        lambda evt, **kw: events.append((kw.get("table"), evt)),
    )

    db = tmp_path / "analytics.db"
    logger = CorrectionLoggerRollback(db)

    target = tmp_path / "file.txt"
    backup = tmp_path / "file.bak"
    target.write_text("a")
    backup.write_text("a")

    # first rollback
    assert logger.auto_rollback(target, backup)
    assert logger.suggest_rollback_strategy(target) == "Standard rollback"

    # second rollback
    target.write_text("b")
    assert logger.auto_rollback(target, backup)
    assert logger.suggest_rollback_strategy(target) == "Automate regression tests for this file."

    # induce failures
    target.unlink()
    logger.auto_rollback(target, None)
    logger.auto_rollback(target, None)
    msg = logger.suggest_rollback_strategy(target)
    assert "audit" in msg.lower()

    assert any(t == "rollback_strategy_history" for t, _ in events)
