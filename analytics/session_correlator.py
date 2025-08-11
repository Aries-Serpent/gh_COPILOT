"""Correlate session provenance and compliance data."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import os
import sqlite3
from typing import Optional


__all__ = ["correlate_session"]


def _db_paths(workspace: Optional[str] = None) -> tuple[Path, Path]:
    ws = Path(workspace or os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    db_dir = ws / "databases"
    return db_dir / "production.db", db_dir / "analytics.db"


def correlate_session(session_id: str, *, workspace: Optional[str] = None) -> Path:
    """Join production and analytics data for ``session_id`` and flag anomalies.

    Any mismatches or compliance issues are written to
    ``monitoring/session_anomalies.log``.
    """

    prod_db, analytics_db = _db_paths(workspace)
    ws = Path(workspace or os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    monitor_dir = ws / "monitoring"
    monitor_dir.mkdir(parents=True, exist_ok=True)
    log_file = monitor_dir / "session_anomalies.log"

    with sqlite3.connect(prod_db) as p_conn, sqlite3.connect(analytics_db) as a_conn:
        p_conn.row_factory = sqlite3.Row
        a_conn.row_factory = sqlite3.Row
        p_row = p_conn.execute(
            "SELECT status, p50_latency, p90_latency, p99_latency, retry_trace FROM session_lifecycle WHERE session_id=?",
            (session_id,),
        ).fetchone()
        a_row = a_conn.execute(
            "SELECT zero_byte_files, status FROM wrap_up_metrics WHERE session_id=?",
            (session_id,),
        ).fetchone()

    anomalies: list[str] = []
    if not p_row or not a_row:
        anomalies.append("missing_records")
    else:
        if a_row["status"] != p_row["status"]:
            anomalies.append("status_mismatch")
        if a_row["zero_byte_files"]:
            anomalies.append("zero_byte_files_present")
        if p_row["p99_latency"] and p_row["p99_latency"] > 1.0:
            anomalies.append("high_latency")
        if p_row["retry_trace"]:
            anomalies.append("retries_detected")

    if anomalies:
        with open(log_file, "a", encoding="utf-8") as fh:
            fh.write(
                f"{datetime.utcnow().isoformat()} {session_id} {';'.join(anomalies)}\n"
            )
    return log_file
