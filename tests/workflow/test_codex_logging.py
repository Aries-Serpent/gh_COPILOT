from pathlib import Path

from utils.codex_logging import log_codex_action, get_codex_history


def test_log_and_retrieve_codex_action(tmp_path: Path) -> None:
    db = tmp_path / "codex.db"
    session_id = "session-1"
    assert log_codex_action(session_id, "run", "stmt1", db_path=db)
    assert log_codex_action(session_id, "finish", "stmt2", db_path=db)

    history = get_codex_history(session_id, db_path=db)
    assert [h["action"] for h in history] == ["run", "finish"]
    assert all("timestamp" in h and "statement" in h for h in history)
