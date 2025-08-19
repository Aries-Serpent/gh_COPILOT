
import json
import os
import sqlite3

from gh_copilot.analytics_logger import log_event, log_sync_operation

def _rowcount(db_path: str) -> int:
    uri = db_path.startswith("file:")
    conn = sqlite3.connect(db_path, uri=uri)
    try:
        cur = conn.execute("SELECT COUNT(*) FROM events")
        return cur.fetchone()[0]
    finally:
        conn.close()

def test_log_event_into_temp_db_respects_test_mode(tmp_path):
    # TEST_MODE on with explicit temp file => safe side-effects
    os.environ["TEST_MODE"] = "1"
    db_file = tmp_path / "events.db"
    os.environ["ANALYTICS_DB_PATH"] = str(db_file)

    log_event("INFO", "unit_event", {"k":"v"})
    assert db_file.exists()
    assert _rowcount(str(db_file)) >= 1

def test_log_sync_operation_payload_and_write(tmp_path):
    os.environ["TEST_MODE"] = "1"
    db_file = tmp_path / "events2.db"
    os.environ["ANALYTICS_DB_PATH"] = str(db_file)

    log_sync_operation("sample.har", 2, "success")
    import sqlite3
    conn = sqlite3.connect(str(db_file))
    try:
        row = conn.execute("SELECT level,event,details FROM events ORDER BY rowid DESC LIMIT 1").fetchone()
        assert row[0] == "INFO"
        assert row[1] == "sync_operation"
        details = json.loads(row[2])
        assert details == {"file_path": "sample.har", "count": 2, "status": "success"}
    finally:
        conn.close()

def test_no_analytics_db_file_when_test_mode_and_no_path(tmp_path, monkeypatch):
    # Ensure cwd is not polluted by a stray analytics.db
    os.environ["TEST_MODE"] = "1"
    os.environ.pop("ANALYTICS_DB_PATH", None)

    # run inside temporary directory
    monkeypatch.chdir(tmp_path)

    # use the logger; it should go to :memory:
    log_event("INFO", "ephemeral_test", {"x": 1})

    # verify analytics.db not created in cwd
    assert not (tmp_path / "analytics.db").exists()
