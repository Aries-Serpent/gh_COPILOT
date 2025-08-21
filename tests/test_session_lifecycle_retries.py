"""Tests for retry logic handling sqlite OperationalError."""

from __future__ import annotations

import sqlite3

from session.session_lifecycle_metrics import end_session, start_session


def test_start_session_retries_on_operational_error(monkeypatch, tmp_path):
    """start_session should retry if the database is temporarily locked."""
    session_id = "retry_start"
    workspace = tmp_path

    real_connect = sqlite3.connect
    calls = {"count": 0}

    def flaky_connect(*args, **kwargs):
        if calls["count"] == 1:
            calls["count"] += 1
            raise sqlite3.OperationalError("database is locked")
        calls["count"] += 1
        return real_connect(*args, **kwargs)

    monkeypatch.setattr(sqlite3, "connect", flaky_connect)

    start_session(session_id, workspace=str(workspace))

    db_path = workspace / "databases" / "production.db"
    with real_connect(db_path) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM session_lifecycle WHERE session_id=?",
            (session_id,),
        ).fetchone()[0]

    assert count == 1


def test_end_session_retries_on_operational_error(monkeypatch, tmp_path):
    """end_session should retry if the database is temporarily locked."""
    session_id = "retry_end"
    workspace = tmp_path

    start_session(session_id, workspace=str(workspace))

    real_connect = sqlite3.connect
    calls = {"count": 0}

    def flaky_connect(*args, **kwargs):
        if calls["count"] == 1:
            calls["count"] += 1
            raise sqlite3.OperationalError("database is locked")
        calls["count"] += 1
        return real_connect(*args, **kwargs)

    monkeypatch.setattr(sqlite3, "connect", flaky_connect)

    end_session(session_id, workspace=str(workspace))

    db_path = workspace / "databases" / "production.db"
    with real_connect(db_path) as conn:
        end_ts = conn.execute(
            "SELECT end_ts FROM session_lifecycle WHERE session_id=?",
            (session_id,),
        ).fetchone()[0]

    assert end_ts is not None
