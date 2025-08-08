"""Tests for session wrap-up validators."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from src.session import SessionManager


def _make_manager(tmp_path: Path) -> SessionManager:
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    (log_dir / "app.log").write_text("ok")
    temp_dir = tmp_path / "tmp"
    temp_dir.mkdir()
    return SessionManager(log_dir, temp_dir)


def test_shutdown_fails_with_open_connections(tmp_path: Path) -> None:
    mgr = _make_manager(tmp_path)
    conn = sqlite3.connect(":memory:")
    mgr.register_connection(conn)
    with pytest.raises(RuntimeError):
        mgr.shutdown()
    conn.close()


def test_shutdown_fails_with_temp_files(tmp_path: Path) -> None:
    mgr = _make_manager(tmp_path)
    temp_file = mgr.temp_dir / "left.tmp"
    temp_file.write_text("bad")
    with pytest.raises(RuntimeError):
        mgr.shutdown()


def test_shutdown_fails_with_empty_logs(tmp_path: Path) -> None:
    mgr = _make_manager(tmp_path)
    empty = mgr.log_dir / "empty.log"
    empty.touch()
    with pytest.raises(RuntimeError):
        mgr.shutdown()


def test_shutdown_passes_when_clean(tmp_path: Path) -> None:
    mgr = _make_manager(tmp_path)
    # No exception means success
    mgr.shutdown()

