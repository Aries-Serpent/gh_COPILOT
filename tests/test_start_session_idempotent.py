"""Tests for repeated start_session calls.

Ensures multiple invocations with the same session_id update
the existing row rather than inserting duplicates.
"""

from __future__ import annotations

import sqlite3

from session.session_lifecycle_metrics import start_session


def test_start_session_multiple_updates(tmp_path):
    """Calling start_session twice should not create duplicate rows."""
    session_id = "duplicate_session"
    workspace = tmp_path

    start_session(session_id, workspace=str(workspace))
    start_session(session_id, workspace=str(workspace))

    db_path = workspace / "databases" / "analytics.db"
    with sqlite3.connect(db_path) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM session_lifecycle WHERE session_id=?",
            (session_id,),
        ).fetchone()[0]
    assert count == 1

