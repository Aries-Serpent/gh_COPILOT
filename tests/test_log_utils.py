import os
import sqlite3

from utils.log_utils import _log_event


def test_log_event_multiple_tables(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_TEST_MODE", "1")
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    db = db_dir / "analytics.db"
    assert _log_event({"msg": "a"}, table="sync_events_log", db_path=db)
    assert _log_event({"msg": "b"}, table="sync_status", db_path=db)
    assert _log_event({"msg": "c"}, table="doc_analysis", db_path=db)
    # analytics.db should not actually be created in test mode
    assert not db.exists()
