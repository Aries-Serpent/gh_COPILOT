import sqlite3
from pathlib import Path

from utils.logging_utils import log_session_event, get_session_history


def test_log_and_retrieve_session_event(tmp_path: Path) -> None:
    db = tmp_path / "analytics.db"
    session_id = "session-1"
    assert log_session_event(session_id, "start", db_path=db)
    assert log_session_event(session_id, "finish", db_path=db)

    history = get_session_history(session_id, db_path=db)
    assert [h["event"] for h in history] == ["start", "finish"]
    assert all("timestamp" in h for h in history)

    with sqlite3.connect(db) as conn:
        rows = conn.execute(
            "SELECT event FROM session_history WHERE session_id=? ORDER BY timestamp",
            (session_id,),
        ).fetchall()
    assert [r[0] for r in rows] == ["start", "finish"]
