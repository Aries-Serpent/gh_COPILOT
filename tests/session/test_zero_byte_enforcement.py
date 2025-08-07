"""Tests for zero-byte file enforcement during session management."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

import unified_session_management_system as usms
from unified_session_management_system import (
    ensure_no_zero_byte_files,
    finalize_session,
)


def test_zero_byte_detection_post_session(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A zero-byte file created after session start triggers failure on exit."""
    db_path = tmp_path / "analytics.db"
    monkeypatch.setattr(usms, "ANALYTICS_DB", db_path)
    target = tmp_path / "late.txt"
    with pytest.raises(RuntimeError):
        with ensure_no_zero_byte_files(tmp_path, "s1"):
            target.touch()
    assert not target.exists()
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT path, phase FROM zero_byte_files").fetchall()
    assert (str(target), "after") in rows


def test_finalize_session_zero_byte_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """``finalize_session`` fails when zero-byte files are present before finalization."""
    db_path = tmp_path / "analytics.db"
    monkeypatch.setattr(usms, "ANALYTICS_DB", db_path)
    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "run.log").write_text("ok")
    bad = tmp_path / "bad.txt"
    bad.touch()
    with pytest.raises(RuntimeError):
        finalize_session(logs, tmp_path, "s2")
    assert not bad.exists()
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT path, phase FROM zero_byte_files").fetchall()
    assert (str(bad), "before") in rows

