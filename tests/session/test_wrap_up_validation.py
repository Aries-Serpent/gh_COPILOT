from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

import unified_session_management_system as usms


def _prepare_logs(tmp_path: Path) -> Path:
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    (log_dir / "app.log").write_text("ok")
    return log_dir


def test_finalize_session_detects_open_handles(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    log_dir = _prepare_logs(tmp_path)
    monkeypatch.setattr(usms, "ANALYTICS_DB", tmp_path / "analytics.db")
    monkeypatch.setattr(usms, "record_codex_action", lambda *a, **k: None)
    handle = (tmp_path / "leak.txt").open("w")
    try:
        with pytest.raises(RuntimeError):
            usms.finalize_session(log_dir, tmp_path, session_id="s1")
    finally:
        handle.close()


def test_finalize_session_detects_open_transactions(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    log_dir = _prepare_logs(tmp_path)
    monkeypatch.setattr(usms, "ANALYTICS_DB", tmp_path / "analytics.db")
    monkeypatch.setattr(usms, "record_codex_action", lambda *a, **k: None)
    conn = sqlite3.connect(":memory:")
    conn.execute("BEGIN")
    try:
        with pytest.raises(RuntimeError):
            usms.finalize_session(log_dir, tmp_path, session_id="s2")
    finally:
        conn.rollback()
        conn.close()

