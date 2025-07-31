from pathlib import Path
import sqlite3
import pytest
from utils.log_utils import _log_event, ensure_tables, log_event


@pytest.mark.parametrize("mode", [False, True])
def test_log_recovery_with_fallback(tmp_path: Path, monkeypatch, mode) -> None:
    monkeypatch.delenv("GH_COPILOT_TEST_MODE", raising=False)
    db = tmp_path / "valid" / "analytics.db"
    ensure_tables(db, ["violation_logs"], test_mode=False)

    log_event({"details": "start"}, table="violation_logs", db_path=db)

    if mode:
        monkeypatch.setenv("GH_COPILOT_TEST_MODE", "1")

    bad_db = tmp_path / "other" / "analytics.db"
    fallback = tmp_path / "fallback.log"

    result = _log_event(
        {"details": "offline"},
        table="violation_logs",
        db_path=bad_db,
        fallback_file=fallback,
        test_mode=False,
    )
    assert result is False
    assert fallback.exists()
    assert fallback.read_text()

    monkeypatch.delenv("GH_COPILOT_TEST_MODE", raising=False)
    log_event({"details": "resume"}, table="violation_logs", db_path=db)
    with sqlite3.connect(db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM violation_logs").fetchone()[0]
    assert count == 2
