"""Tests for session wrap-up validators."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from src.session import SessionManager
from src.session.validators import validate_lifecycle


def _make_manager(tmp_path: Path) -> SessionManager:
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    (log_dir / "app.log").write_text("ok")
    temp_dir = tmp_path / "tmp"
    temp_dir.mkdir()
    session_dir = tmp_path / "sessions"
    session_dir.mkdir()
    return SessionManager(log_dir, temp_dir, session_dir)


def test_shutdown_fails_with_open_connections(tmp_path: Path) -> None:
    mgr = _make_manager(tmp_path)
    conn = sqlite3.connect(":memory:")
    mgr.register_connection(conn)
    with pytest.raises(RuntimeError):
        mgr.shutdown()
    conn.close()


def test_shutdown_fails_with_uncommitted_transactions(tmp_path: Path) -> None:
    mgr = _make_manager(tmp_path)
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE t (x int)")
    conn.execute("INSERT INTO t VALUES (1)")
    mgr.register_connection(conn)
    with pytest.raises(RuntimeError):
        mgr.shutdown()
    conn.rollback()
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


def test_shutdown_fails_with_orphaned_sessions(tmp_path: Path) -> None:
    mgr = _make_manager(tmp_path)
    session_file = mgr.session_dir / "session-abc.json"
    session_file.write_text("{}")
    with pytest.raises(RuntimeError):
        mgr.shutdown()


def test_shutdown_passes_when_clean(tmp_path: Path) -> None:
    mgr = _make_manager(tmp_path)
    # No exception means success
    mgr.shutdown()


def test_validate_lifecycle_reports_all(tmp_path: Path) -> None:
    mgr = _make_manager(tmp_path)
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE t (x int)")
    conn.execute("INSERT INTO t VALUES (1)")
    (mgr.temp_dir / "left.tmp").write_text("bad")
    (mgr.log_dir / "empty.log").touch()
    (mgr.session_dir / "session-abc.json").write_text("{}")

    issues = validate_lifecycle(
        [conn],
        log_dir=mgr.log_dir,
        temp_dir=mgr.temp_dir,
        session_dir=mgr.session_dir,
    )

    assert set(issues) == {
        "open_connections",
        "uncommitted_transactions",
        "temp_files",
        "empty_logs",
        "orphaned_sessions",
    }

    conn.rollback()
    conn.close()
