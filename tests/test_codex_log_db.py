"""Tests for codex_log_db utilities."""

import sqlite3

from utils import codex_log_db


def test_init_db_creates_codex_actions(tmp_path, monkeypatch):
    db_file = tmp_path / "codex_log.db"
    monkeypatch.setattr(codex_log_db, "CODEX_LOG_DB", db_file)
    codex_log_db.init_db()
    assert db_file.exists()
    with sqlite3.connect(db_file) as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='codex_actions'"
        )
        assert cursor.fetchone() is not None


def test_log_codex_action_inserts_row(tmp_path, monkeypatch):
    db_file = tmp_path / "codex_log.db"
    monkeypatch.setattr(codex_log_db, "CODEX_LOG_DB", db_file)
    codex_log_db.log_codex_action("s1", "act", "stmt", "meta")
    with sqlite3.connect(db_file) as conn:
        rows = conn.execute(
            "SELECT session_id, action, statement, metadata FROM codex_actions"
        ).fetchall()
    assert rows == [("s1", "act", "stmt", "meta")]

