from __future__ import annotations

import sqlite3
from pathlib import Path

from session.session_lifecycle_metrics import start_session


def _session_count(db_path: Path, session_id: str) -> int:
    with sqlite3.connect(db_path) as conn:
        return conn.execute(
            "SELECT COUNT(*) FROM session_lifecycle WHERE session_id=?",
            (session_id,),
        ).fetchone()[0]


def test_start_session_creates_db_when_missing(tmp_path: Path) -> None:
    session_id = "missing_db"
    workspace = tmp_path
    db_path = workspace / "databases" / "production.db"
    assert not db_path.exists()

    start_session(session_id, workspace=str(workspace))

    assert db_path.exists()
    assert _session_count(db_path, session_id) == 1


def test_start_session_recovers_from_corrupt_db(tmp_path: Path) -> None:
    session_id = "corrupt_db"
    workspace = tmp_path
    db_path = workspace / "databases" / "production.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db_path.write_text("not-a-db")

    start_session(session_id, workspace=str(workspace))

    backup = db_path.with_suffix(db_path.suffix + ".corrupt")
    assert backup.exists()
    assert _session_count(db_path, session_id) == 1
