"""Tests for session_logger module."""

import sqlite3
import uuid
from pathlib import Path

from codex.logging.session_logger import SessionLogger


def test_session_logger_inserts_rows(tmp_path: Path) -> None:
    db_path = tmp_path / "test_codex_session_log.db"
    sid = str(uuid.uuid4())
    logger = SessionLogger(db_path=str(db_path), session_id=sid)
    with logger.session_context():
        logger.log_message("user", "Hello")
        logger.log_message("assistant", "Hi")

    con = sqlite3.connect(str(db_path))
    rows = list(
        con.execute(
            "SELECT session_id, role, message FROM session_events WHERE session_id = ?", (sid,)
        )
    )
    assert len(rows) >= 3
    roles = {r[1] for r in rows}
    assert {"user", "assistant"} <= roles

