import sqlite3
from pathlib import Path

import pytest

from utils.codex_logging import get_codex_history, log_codex_action


def test_log_and_retrieve_codex_action(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "utils.codex_logging.validate_enterprise_operation", lambda *_a, **_k: True
    )
    monkeypatch.setattr(
        "enterprise_modules.database_utils.validate_enterprise_operation",
        lambda *_a, **_k: True,
    )
    db = tmp_path / "codex.db"
    session_id = "session-1"
    assert log_codex_action(session_id, "run", "stmt1", db_path=db)
    assert log_codex_action(session_id, "finish", "stmt2", db_path=db)

    history = get_codex_history(session_id, db_path=db)
    assert [h["action"] for h in history] == ["run", "finish"]
    assert [h["statement"] for h in history] == ["stmt1", "stmt2"]
    assert all("timestamp" in h for h in history)

    with sqlite3.connect(db) as conn:
        rows = conn.execute(
            "SELECT action, statement FROM codex_log WHERE session_id=? ORDER BY timestamp",
            (session_id,),
        ).fetchall()
    assert rows == [("run", "stmt1"), ("finish", "stmt2")]
