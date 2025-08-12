#!/usr/bin/env python3
"""System health monitoring utilities stored in analytics.db."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Dict, Optional

from types import SimpleNamespace

try:  # pragma: no cover - psutil optional in some environments
    import psutil  # type: ignore
except Exception:  # pragma: no cover - fallback stub
    psutil = SimpleNamespace(
        cpu_percent=lambda interval=0: 0.0,
        virtual_memory=lambda: SimpleNamespace(percent=0.0),
        disk_usage=lambda _p: SimpleNamespace(percent=0.0),
        net_io_counters=lambda: SimpleNamespace(bytes_sent=0, bytes_recv=0),
    )

from quantum_algorithm_library_expansion import quantum_score_stub

WORKSPACE_ROOT = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
DB_PATH = WORKSPACE_ROOT / "analytics.db"

CPU_ALERT_THRESHOLD = 85.0
MEMORY_ALERT_THRESHOLD = 90.0
DISK_ALERT_THRESHOLD = 90.0
ANOMALY_DEVIATION = 20.0

__all__ = [
    "record_system_health",
    "recent_average",
    "gather_metrics",
    "ensure_table",
    "check_alerts",
    "ml_anomaly_detect",
    "quantum_hook",
]


def ensure_table(conn: sqlite3.Connection) -> None:
    """Ensure the system_health table exists and has quantum_score."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS system_health (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            cpu_percent REAL,
            memory_percent REAL,
            disk_percent REAL,
            net_bytes_sent INTEGER,
            net_bytes_recv INTEGER,
            quantum_score REAL
        )
        """
    )
    # Add column if table existed without quantum_score
    try:
        conn.execute("ALTER TABLE system_health ADD COLUMN quantum_score REAL")
    except sqlite3.OperationalError:
        pass


def gather_metrics() -> Dict[str, float]:
    """Collect current system metrics."""
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
        "net_bytes_sent": psutil.net_io_counters().bytes_sent,
        "net_bytes_recv": psutil.net_io_counters().bytes_recv,
    }


def ml_anomaly_detect(metrics: Dict[str, float]) -> bool:
    """Naive ML-based anomaly detector placeholder.

    This uses a simple deviation heuristic until a model is plugged in.
    """

    values = [metrics["cpu_percent"], metrics["memory_percent"], metrics["disk_percent"]]
    avg = sum(values) / len(values)
    return any(abs(v - avg) > ANOMALY_DEVIATION for v in values)


def quantum_hook(metrics: Dict[str, float]) -> float:
    """Compute a quantum-inspired score for system metrics."""

    values = [metrics["cpu_percent"], metrics["memory_percent"], metrics["disk_percent"]]
    score = quantum_score_stub(values)
    metrics["quantum_score"] = score
    return score


def check_alerts(metrics: Dict[str, float]) -> Dict[str, bool]:
    """Return ``True`` for metrics exceeding alert thresholds."""
    alerts = {
        "cpu": metrics["cpu_percent"] > CPU_ALERT_THRESHOLD,
        "memory": metrics["memory_percent"] > MEMORY_ALERT_THRESHOLD,
        "disk": metrics["disk_percent"] > DISK_ALERT_THRESHOLD,
    }
    alerts["ml_anomaly"] = ml_anomaly_detect(metrics)
    quantum_hook(metrics)
    return alerts


def record_system_health(db_path: Optional[Path] = None) -> Dict[str, float]:
    """Record current system health metrics and return them."""
    metrics = gather_metrics()
    quantum_hook(metrics)
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
                net_bytes_recv,
                quantum_score
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                metrics["cpu_percent"],
                metrics["memory_percent"],
                metrics["disk_percent"],
                metrics["net_bytes_sent"],
                metrics["net_bytes_recv"],
                metrics["quantum_score"],
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
                   AVG(net_bytes_recv),
                   AVG(quantum_score)
            FROM (
                SELECT * FROM system_health ORDER BY id DESC LIMIT ?
            )
            """,
            (n,),
        )
        row = cur.fetchone() or (0, 0, 0, 0, 0, 0)
        return {
            "avg_cpu_percent": row[0] or 0.0,
            "avg_memory_percent": row[1] or 0.0,
            "avg_disk_percent": row[2] or 0.0,
            "avg_net_bytes_sent": row[3] or 0.0,
            "avg_net_bytes_recv": row[4] or 0.0,
            "avg_quantum_score": row[5] or 0.0,
        }


if __name__ == "__main__":
    results = record_system_health()
    print(results)
