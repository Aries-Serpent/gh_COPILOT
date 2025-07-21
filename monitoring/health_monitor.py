#!/usr/bin/env python3
"""System health monitoring utilities stored in analytics.db."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Dict, Optional

import psutil

WORKSPACE_ROOT = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
DB_PATH = WORKSPACE_ROOT / "analytics.db"

__all__ = [
    "record_system_health",
    "recent_average",
    "gather_metrics",
    "ensure_table",
]


def ensure_table(conn: sqlite3.Connection) -> None:
    """Ensure the system_health table exists."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS system_health (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            cpu_percent REAL,
            memory_percent REAL,
            disk_percent REAL,
            net_bytes_sent INTEGER,
            net_bytes_recv INTEGER
        )
        """
    )


def gather_metrics() -> Dict[str, float]:
    """Collect current system metrics."""
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
        "net_bytes_sent": psutil.net_io_counters().bytes_sent,
        "net_bytes_recv": psutil.net_io_counters().bytes_recv,
    }


def record_system_health(db_path: Optional[Path] = None) -> Dict[str, float]:
    """Record current system health metrics and return them."""
    metrics = gather_metrics()
    path = db_path or DB_PATH
    with sqlite3.connect(path) as conn:
        ensure_table(conn)
        conn.execute(
            """
            INSERT INTO system_health (
                cpu_percent,
                memory_percent,
                disk_percent,
                net_bytes_sent,
                net_bytes_recv
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                metrics["cpu_percent"],
                metrics["memory_percent"],
                metrics["disk_percent"],
                metrics["net_bytes_sent"],
                metrics["net_bytes_recv"],
            ),
        )
        conn.commit()
    return metrics


def recent_average(n: int = 10, db_path: Optional[Path] = None) -> Dict[str, float]:
    """Return averages for the most recent ``n`` health records."""
    path = db_path or DB_PATH
    with sqlite3.connect(path) as conn:
        ensure_table(conn)
        cur = conn.execute(
            """
            SELECT AVG(cpu_percent),
                   AVG(memory_percent),
                   AVG(disk_percent),
                   AVG(net_bytes_sent),
                   AVG(net_bytes_recv)
            FROM (
                SELECT * FROM system_health ORDER BY id DESC LIMIT ?
            )
            """,
            (n,),
        )
        row = cur.fetchone() or (0, 0, 0, 0, 0)
        return {
            "avg_cpu_percent": row[0] or 0.0,
            "avg_memory_percent": row[1] or 0.0,
            "avg_disk_percent": row[2] or 0.0,
            "avg_net_bytes_sent": row[3] or 0.0,
            "avg_net_bytes_recv": row[4] or 0.0,
        }


if __name__ == "__main__":
    results = record_system_health()
    print(results)
