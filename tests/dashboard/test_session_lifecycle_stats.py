from pathlib import Path
import sqlite3

from dashboard.enterprise_dashboard import session_lifecycle_stats


def _create_db(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE session_lifecycle("\
            "session_id TEXT, duration_seconds REAL, status TEXT, "\
            "zero_byte_violations INTEGER, end_ts INTEGER)"
        )
        conn.executemany(
            "INSERT INTO session_lifecycle("\
            "session_id, duration_seconds, status, zero_byte_violations, end_ts) "\
            "VALUES (?,?,?,?,?)",
            [
                ("a", 1.0, "success", 0, 1),
                ("b", 3.0, "success", 0, 2),
            ],
        )
        conn.commit()


def test_session_lifecycle_stats(tmp_path: Path) -> None:
    db = tmp_path / "analytics.db"
    _create_db(db)
    stats = session_lifecycle_stats(db)
    assert stats["count"] == 2
    assert stats["avg_duration"] == 2.0
    assert stats["success_rate"] == 1.0
    assert stats["last_duration"] == 3.0
    assert stats["last_status"] == "success"
    assert stats["last_zero_byte_violations"] == 0
