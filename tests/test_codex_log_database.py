"""Tests for the Codex session log database."""

from __future__ import annotations

from pathlib import Path
import tempfile

import sqlite3
import pytest
from utils import codex_log_database as cldb


def test_log_and_fetch() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "codex_test.db"
        cldb.log_codex_event("action", "statement", session_id="s1", db_path=db_path)
        events = cldb.fetch_codex_events(session_id="s1", db_path=db_path)
        assert events and events[0]["action"] == "action"
        assert events[0]["statement"] == "statement"


def test_ensure_db_recovers_from_corruption(tmp_path: Path) -> None:
    db_path = tmp_path / "corrupt.db"
    db_path.write_text("not a database")
    cldb._ensure_db(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute("SELECT 1")


def test_log_codex_event_db_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    db_path = tmp_path / "db.sqlite"
    cldb._ensure_db(db_path)

    def boom(*args, **kwargs):
        raise sqlite3.DatabaseError("fail")

    monkeypatch.setattr(sqlite3, "connect", boom)
    monkeypatch.setattr(cldb, "_ensure_db", lambda _db_path: None)
    with pytest.raises(RuntimeError, match="Failed to log Codex event"):
        cldb.log_codex_event("a", "b", db_path=db_path)


def test_fetch_codex_events_db_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    db_path = tmp_path / "db.sqlite"
    cldb._ensure_db(db_path)

    def boom(*args, **kwargs):
        raise sqlite3.DatabaseError("fail")

    monkeypatch.setattr(sqlite3, "connect", boom)
    monkeypatch.setattr(cldb, "_ensure_db", lambda _db_path: None)
    with pytest.raises(RuntimeError, match="Failed to fetch Codex events"):
        cldb.fetch_codex_events(db_path=db_path)

