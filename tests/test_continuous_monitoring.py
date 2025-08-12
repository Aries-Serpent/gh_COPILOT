#!/usr/bin/env python3
"""Tests scheduled monitoring helpers."""

import os
import sqlite3
import threading
import time

from ghc_monitoring.log_error_notifier import schedule_log_monitoring
from ghc_monitoring.performance_tracker import (
    schedule_metrics_push,
    track_query_time,
)


def test_schedule_log_monitoring_records_notifications(tmp_path):
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    db = db_dir / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS log_errors (file TEXT, error TEXT, timestamp TEXT)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS log_notifications (errors_found INTEGER, timestamp TEXT)"
        )
    log_file = tmp_path / "app.log"
    log_file.write_text("INFO ok\nERROR boom\n")
    stop = threading.Event()
    thread = schedule_log_monitoring([log_file], 0.1, db_path=db, stop_event=stop)
    time.sleep(0.2)
    stop.set()
    thread.join(timeout=1)
    with sqlite3.connect(db) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM log_notifications")
        assert cur.fetchone()[0] > 0


def test_schedule_metrics_push_inserts_summary(tmp_path):
    db = tmp_path / "analytics.db"
    track_query_time("q1", 10.0, db_path=db)
    stop = threading.Event()
    thread = schedule_metrics_push(0.1, db_path=db, stop_event=stop)
    time.sleep(0.2)
    stop.set()
    thread.join(timeout=1)
    with sqlite3.connect(db) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM performance_summary")
        assert cur.fetchone()[0] > 0
