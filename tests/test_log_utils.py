import sqlite3

from utils.log_utils import _log_event


def test_log_event_multiple_tables(tmp_path):
    db = tmp_path / "analytics.db"
    assert _log_event({"msg": "a"}, table="sync_events_log", db_path=db)
    assert _log_event({"msg": "b"}, table="sync_status", db_path=db)
    assert _log_event({"msg": "c"}, table="doc_analysis", db_path=db)
    with sqlite3.connect(db) as conn:
        for tbl in ("sync_events_log", "sync_status", "doc_analysis"):
            count = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
            assert count == 1
