import sqlite3

import pytest

from session.session_lifecycle_metrics import (
    end_session,
    record_latency,
    record_retry,
    start_session,
)
from unified_session_management_system import ensure_no_zero_byte_files
from analytics.session_correlator import correlate_session


def test_latency_capture_and_correlation(tmp_path):
    workspace = tmp_path
    db_dir = workspace / "databases"
    db_dir.mkdir()
    prod_db = db_dir / "production.db"
    analytics_db = db_dir / "analytics.db"
    sqlite3.connect(prod_db).close()
    sqlite3.connect(analytics_db).close()

    session_id = "s1"
    start_session(session_id, workspace=str(workspace))
    for val in (0.1, 0.2, 0.4):
        record_latency(session_id, val, workspace=str(workspace))
    record_retry(session_id, "retry1", workspace=str(workspace))

    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """CREATE TABLE wrap_up_metrics (
            session_id TEXT, zero_byte_files INTEGER, status TEXT, duration_seconds REAL)
            """
        )
        conn.execute(
            "INSERT INTO wrap_up_metrics VALUES (?, ?, ?, ?)",
            (session_id, 1, "failed", 0.5),
        )
        conn.commit()

    end_session(session_id, workspace=str(workspace))

    with sqlite3.connect(prod_db) as conn:
        row = conn.execute(
            "SELECT p50_latency, p90_latency, p99_latency, retry_trace FROM session_lifecycle WHERE session_id=?",
            (session_id,),
        ).fetchone()
    assert row[0] == pytest.approx(0.2)
    assert row[1] == pytest.approx(0.4)
    assert row[2] == pytest.approx(0.4)
    assert "retry1" in row[3]

    bad_dir = workspace / "backup"
    bad_dir.mkdir()
    with pytest.raises(RuntimeError):
        with ensure_no_zero_byte_files(bad_dir, session_id):
            pass

    log_file = correlate_session(session_id, workspace=str(workspace))
    assert log_file.exists()
    content = log_file.read_text()
    assert session_id in content
    assert "status_mismatch" in content
