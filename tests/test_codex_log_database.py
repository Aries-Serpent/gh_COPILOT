"""Tests for the Codex session log database."""

from __future__ import annotations

from pathlib import Path
import tempfile

from utils.codex_log_database import fetch_codex_events, log_codex_event


def test_log_and_fetch() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "codex_test.db"
        log_codex_event("action", "statement", session_id="s1", db_path=db_path)
        events = fetch_codex_events(session_id="s1", db_path=db_path)
        assert events and events[0]["action"] == "action"
        assert events[0]["statement"] == "statement"

