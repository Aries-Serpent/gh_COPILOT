"""Tests for the ``codex_action_logger`` module."""

import json
import sqlite3

from utils import codex_action_logger


def test_init_creates_table(tmp_path, monkeypatch):
    """``init_codex_log_db`` should create the ``codex_logs`` table."""

    db_file = tmp_path / "codex_logs.db"
    monkeypatch.setattr(codex_action_logger, "_CODEX_LOG_DB", db_file)
    monkeypatch.setattr(codex_action_logger, "_SESSION_ID", None)

    codex_action_logger.init_codex_log_db("session-1")

    assert db_file.exists()
    with sqlite3.connect(db_file) as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='codex_logs'"
        )
        assert cursor.fetchone() is not None


def test_record_and_finalize(tmp_path, monkeypatch):
    """Actions should be recorded and the DB path returned on finalize."""

    db_file = tmp_path / "codex_logs.db"
    monkeypatch.setattr(codex_action_logger, "_CODEX_LOG_DB", db_file)
    monkeypatch.setattr(codex_action_logger, "_SESSION_ID", None)

    codex_action_logger.init_codex_log_db("s1")
    codex_action_logger.record_codex_action(
        "action", "statement", metadata={"foo": "bar"}
    )
    path = codex_action_logger.finalize_codex_log_db()

    assert path == db_file
    with sqlite3.connect(db_file) as conn:
        rows = conn.execute(
            "SELECT session_id, action, statement, metadata FROM codex_logs"
        ).fetchall()

    assert rows == [("s1", "action", "statement", json.dumps({"foo": "bar"}))]

