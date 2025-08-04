from pathlib import Path
import sqlite3

from scripts.database.add_legacy_cleanup_log import (
    ensure_legacy_cleanup_log,
    log_cleanup_event,
)


def test_log_cleanup_event(tmp_path: Path, monkeypatch) -> None:
    db = tmp_path / "databases" / "analytics.db"
    ensure_legacy_cleanup_log(db)
    monkeypatch.setenv("GH_COPILOT_TEST_MODE", "0")
    log_cleanup_event("demo.py", action="archived", reason="test", db_path=db)
    with sqlite3.connect(db) as conn:
        row = conn.execute(
            "SELECT file, action, reason FROM legacy_cleanup_log"
        ).fetchone()
    assert row == ("demo.py", "archived", "test")
