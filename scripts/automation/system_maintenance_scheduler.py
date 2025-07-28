#!/usr/bin/env python3
"""System maintenance scheduler for continuous operation."""

# pyright: reportMissingImports=false

from __future__ import annotations

import os
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

import schedule

from scripts.monitoring.continuous_operation_monitor import (
    ContinuousOperationMonitor,
)
from scripts.utilities import self_healing_self_learning_system as shs
from scripts.wlc_session_manager import finalize_session_entry, start_session_entry


def _ensure_job_table(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS system_maintenance_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_name TEXT,
                start_time TEXT,
                end_time TEXT,
                status TEXT
            )
            """
        )
        conn.commit()


def _log_job(db_path: Path, job_name: str, start: datetime, end: datetime, status: str) -> None:
    _ensure_job_table(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO system_maintenance_jobs (job_name, start_time, end_time, status) VALUES (?, ?, ?, ?)",
            (job_name, start.isoformat(), end.isoformat(), status),
        )
        conn.commit()


def _run_self_healing(workspace: Path) -> None:
    shs.main()


def _run_monitor_once(workspace: Path) -> None:
    monitor = ContinuousOperationMonitor(
        monitor_interval=60,
        log_db=str(workspace / "analytics.db"),
        verbose=False,
    )
    metrics = monitor._get_system_metrics()
    monitor._write_metrics(metrics)


def maintenance_cycle(workspace: Path) -> None:
    analytics_db = workspace / "analytics.db"
    production_db = workspace / "databases" / "production.db"
    start = datetime.now(timezone.utc)
    status = "SUCCESS"
    entry_id = None
    try:
        with sqlite3.connect(production_db) as conn:
            entry_id = start_session_entry(conn)
        _run_self_healing(workspace)
        _run_monitor_once(workspace)
        if entry_id is not None:
            with sqlite3.connect(production_db) as conn:
                finalize_session_entry(conn, entry_id, 1.0)
    except Exception as exc:  # noqa: BLE001
        status = f"FAILED_{type(exc).__name__}"
        if entry_id is not None:
            with sqlite3.connect(production_db) as conn:
                finalize_session_entry(conn, entry_id, 0.0, error=str(exc))
    end = datetime.now(timezone.utc)
    _log_job(analytics_db, "maintenance_cycle", start, end, status)


def start_scheduler(interval_minutes: int = 60) -> None:
    workspace = Path(os.environ.get("GH_COPILOT_WORKSPACE", ".")).resolve()
    schedule.every(interval_minutes).minutes.do(maintenance_cycle, workspace)
    print(f"[INFO] Maintenance scheduler running every {interval_minutes} minutes")
    while True:
        schedule.run_pending()
        time.sleep(1)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run system maintenance scheduler")
    parser.add_argument("--interval", type=int, default=60, help="Minutes between cycles")
    args = parser.parse_args()
    start_scheduler(args.interval)


if __name__ == "__main__":
    main()
