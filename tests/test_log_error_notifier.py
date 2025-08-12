#!/usr/bin/env python3
"""Tests for :mod:`monitoring.log_error_notifier`."""

import importlib
import sqlite3
import sys
from pathlib import Path

# Ensure the repository root is on ``sys.path`` so that the local ``monitoring``
# package is imported instead of any third-party module with the same name.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Remove any preloaded third-party ``monitoring`` module to avoid conflicts.
sys.modules.pop("monitoring", None)

notifier = importlib.import_module("monitoring.log_error_notifier")


def _prepare_db(tmp_path: Path) -> Path:
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    db = db_dir / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS log_errors (file TEXT, error TEXT, timestamp TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS log_notifications (errors_found INTEGER, timestamp TEXT)")
    return db


def test_monitor_logs_detects_errors(tmp_path, monkeypatch):
    db = _prepare_db(tmp_path)
    log_file = tmp_path / "app.log"
    log_file.write_text("INFO Start\nERROR Failure occurred\n")

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))

    count = notifier.monitor_logs([log_file], db_path=db)
    assert count == 1
    with sqlite3.connect(db) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM log_errors")
        assert cur.fetchone()[0] == 1
        cur = conn.execute("SELECT COUNT(*) FROM log_notifications")
        assert cur.fetchone()[0] == 1


def test_monitor_logs_no_errors(tmp_path, monkeypatch):
    """No entries are written when logs contain no errors."""

    db = _prepare_db(tmp_path)
    log_file = tmp_path / "app.log"
    log_file.write_text("INFO Start\nINFO Still running\n")

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))

    count = notifier.monitor_logs([log_file], db_path=db)
    assert count == 0
    with sqlite3.connect(db) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM log_errors")
        assert cur.fetchone()[0] == 0
        cur = conn.execute("SELECT COUNT(*) FROM log_notifications")
        assert cur.fetchone()[0] == 0
