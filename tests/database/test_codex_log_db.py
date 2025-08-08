import sqlite3

from utils import codex_log_db


def test_init_db_creates_table(tmp_path, monkeypatch):
    test_db = tmp_path / "codex_log.db"
    monkeypatch.setattr(codex_log_db, "CODEX_LOG_DB", test_db)
    codex_log_db.init_codex_log_db()
    assert test_db.exists()
    with sqlite3.connect(test_db) as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='codex_actions'"
        )
        assert cursor.fetchone() is not None


def test_record_codex_action_inserts_row(tmp_path, monkeypatch):
    test_db = tmp_path / "codex_log.db"
    monkeypatch.setattr(codex_log_db, "CODEX_LOG_DB", test_db)
    codex_log_db.record_codex_action("s1", "act", "stmt", "meta")
    with sqlite3.connect(test_db) as conn:
        cursor = conn.execute(
            "SELECT session_id, action, statement, metadata FROM codex_actions"
        )
        rows = cursor.fetchall()
        assert rows == [("s1", "act", "stmt", "meta")]
