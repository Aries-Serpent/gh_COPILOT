import sqlite3
import tempfile
from pathlib import Path

from utils.analytics_logger import log_analytics_event, get_run_id


def _prepare_temp_db():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    conn = sqlite3.connect(tmp.name)
    with conn:
        conn.execute(
            "CREATE TABLE events (event_time TEXT, level TEXT, event TEXT, details TEXT)"
        )
    conn.close()
    return Path(tmp.name)


def test_log_analytics_event_inserts_row():
    db = _prepare_temp_db()
    try:
        ok = log_analytics_event(
            db,
            level="INFO",
            step="compare_schema",
            phase="schema_diff_reconcile",
            event="enter_function",
            details={"unit_test": True},
            run_id=get_run_id(),
        )
        assert ok, "Expected insert to succeed"
        conn = sqlite3.connect(db)
        rows = list(
            conn.execute(
                "SELECT event_time, level, event, details FROM events"
            )
        )
        conn.close()
        assert len(rows) == 1
        assert rows[0][1] == "INFO"
        assert rows[0][2] == "enter_function"
    finally:
        if db.exists():
            db.unlink()
