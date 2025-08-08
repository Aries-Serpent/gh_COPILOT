"""Tests for Codex logging utilities."""

import sqlite3
from pathlib import Path
import sys
import types


class DummyTqdm(list):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def update(self, *args, **kwargs):
        return None


def _tqdm(iterable=None, *args, **kwargs):
    return DummyTqdm(iterable or [])


sys.modules.setdefault("tqdm", types.SimpleNamespace(tqdm=_tqdm))
from utils import codex_log_db


def test_init_creates_table(tmp_path, monkeypatch):
    """``init_codex_log_db`` should create the ``codex_actions`` table."""

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    db_file = tmp_path / "codex_log.db"
    session_file = tmp_path / "codex_session_logs.db"
    monkeypatch.setattr(codex_log_db, "CODEX_LOG_DB", db_file)
    monkeypatch.setattr(codex_log_db, "CODEX_SESSION_LOG_DB", session_file)

    codex_log_db.init_codex_log_db()

    assert db_file.exists()
    with sqlite3.connect(db_file) as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='codex_actions'"
        )
        assert cursor.fetchone() is not None


def test_record_and_finalize(tmp_path, monkeypatch):
    """Actions should be recorded and the DB staged on finalize."""

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backup"))

    db_file = tmp_path / "codex_log.db"
    session_file = tmp_path / "codex_session_logs.db"
    monkeypatch.setattr(codex_log_db, "CODEX_LOG_DB", db_file)
    monkeypatch.setattr(codex_log_db, "CODEX_SESSION_LOG_DB", session_file)

    calls: list[list[str]] = []

    def fake_run(cmd, cwd=None, check=False):
        calls.append(cmd)
        class Result:
            returncode = 0
        return Result()

    monkeypatch.setattr(codex_log_db.subprocess, "run", fake_run)

    codex_log_db.init_codex_log_db()
    codex_log_db.record_codex_action("s1", "action", "statement", "meta")
    src = codex_log_db.finalize_codex_log_db()

    assert src == db_file
    assert session_file.exists()

    with sqlite3.connect(db_file) as conn:
        rows = conn.execute(
            "SELECT session_id, action, statement, metadata FROM codex_actions"
        ).fetchall()

    assert rows == [("s1", "action", "statement", "meta")]
    assert any(
        cmd[:2] == ["git", "add"]
        and str(Path(cmd[-2])) == str(db_file.relative_to(tmp_path))
        and str(Path(cmd[-1])) == str(session_file.relative_to(tmp_path))
        for cmd in calls
    )

