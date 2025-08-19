"""Tests for repeated start_session calls.

Ensures multiple invocations with the same session_id do not
insert duplicates or modify the original start timestamp.
"""

from __future__ import annotations

import sqlite3

from session.session_lifecycle_metrics import start_session


def test_start_session_multiple_updates(tmp_path):
    """Calling start_session twice should keep one row and preserve start time."""
    session_id = "duplicate_session"
    workspace = tmp_path

    start_session(session_id, workspace=str(workspace))
    db_path = workspace / "databases" / "production.db"
    with sqlite3.connect(db_path) as conn:
        first_ts = conn.execute(
            "SELECT start_ts FROM session_lifecycle WHERE session_id=?",
            (session_id,),
        ).fetchone()[0]

    start_session(session_id, workspace=str(workspace))

    with sqlite3.connect(db_path) as conn:
        count, min_ts, max_ts = conn.execute(
            "SELECT COUNT(*), MIN(start_ts), MAX(start_ts) FROM session_lifecycle WHERE session_id=?",
            (session_id,),
        ).fetchone()

    assert count == 1
    assert min_ts == max_ts == first_ts
