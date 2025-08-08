"""Tests for codex_log_db helper functions."""

import json
import sqlite3

from utils import codex_log_db


def test_init_db_creates_tables(tmp_path, monkeypatch):
    """init_codex_log_db should create required tables."""
    db_file = tmp_path / "codex_log.db"
    monkeypatch.setattr(codex_log_db, "CODEX_LOG_DB", db_file)

    codex_log_db.init_codex_log_db()

    assert db_file.exists()
    with sqlite3.connect(db_file) as conn:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'",
            )
        }
    assert {"codex_actions", "codex_log"} <= tables


def test_record_codex_action_inserts_row(tmp_path, monkeypatch):
    """record_codex_action should insert a row into codex_actions."""
    db_file = tmp_path / "codex_log.db"
    monkeypatch.setattr(codex_log_db, "CODEX_LOG_DB", db_file)

    codex_log_db.record_codex_action("s1", "act", "stmt", "meta")

    with sqlite3.connect(db_file) as conn:
        rows = conn.execute(
            "SELECT session_id, action, statement, metadata FROM codex_actions",
        ).fetchall()

    assert rows == [("s1", "act", "stmt", "meta")]


def test_record_codex_action_serializes_metadata(tmp_path, monkeypatch):
    """Dictionary metadata should be stored as JSON and timestamp in UTC."""
    db_file = tmp_path / "codex_log.db"
    monkeypatch.setattr(codex_log_db, "CODEX_LOG_DB", db_file)

    codex_log_db.record_codex_action("s1", "act", "stmt", {"a": 1})

    with sqlite3.connect(db_file) as conn:
        ts, metadata = conn.execute(
            "SELECT ts, metadata FROM codex_actions",
        ).fetchone()

    assert ts.endswith("+00:00")
    assert json.loads(metadata) == {"a": 1}


def test_finalize_codex_log_db_copies_db(tmp_path, monkeypatch):
    """finalize_codex_log_db should copy codex_log.db to destination."""
    src = tmp_path / "codex_log.db"
    dest = tmp_path / "codex_session_logs.db"
    monkeypatch.setattr(codex_log_db, "CODEX_LOG_DB", src)
    monkeypatch.setattr(codex_log_db, "CODEX_SESSION_LOG_DB", dest)
    monkeypatch.setattr(
        codex_log_db.CrossPlatformPathManager,
        "get_workspace_path",
        lambda: tmp_path,
    )

    calls = []

    def fake_run(cmd, cwd=None, check=True):
        calls.append(cmd)
        class Result:
            returncode = 0
        return Result()

    monkeypatch.setattr(codex_log_db.subprocess, "run", fake_run)

    codex_log_db.log_codex_action("s1", "act", "stmt")
    copied = codex_log_db.finalize_codex_log_db()

    assert copied == dest
    assert dest.exists()
    with sqlite3.connect(dest) as conn:
        rows = conn.execute(
            "SELECT session_id, action, statement FROM codex_actions",
        ).fetchall()

    assert rows == [("s1", "act", "stmt")]
    assert any(cmd[:2] == ["git", "add"] for cmd in calls)

