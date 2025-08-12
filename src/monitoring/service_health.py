"""Service health and uptime monitoring utilities."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Dict, Optional

import requests

from web_gui.monitoring.alerting.alert_manager import trigger_alert

WORKSPACE_ROOT = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
DB_PATH = WORKSPACE_ROOT / "analytics.db"

# Default service endpoints used by :func:`run_health_checks`.
SERVICES = {
    "sync_engine": "http://localhost:8000/health",
    "dashboard": "http://localhost:5000/api/health",
    "anomaly": "http://localhost:5001/health",
}


def _ensure_table(conn: sqlite3.Connection) -> None:
    """Ensure the ``service_uptime`` table exists."""

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS service_uptime (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT NOT NULL,
            status TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def check_service(
    name: str,
    url: str,
    *,
    db_path: Optional[Path] = None,
) -> bool:
    """Return ``True`` when ``url`` responds with HTTP 200.

    Results are recorded in ``service_uptime`` and a critical alert is
    triggered when the service is unreachable.
    """

    try:  # pragma: no cover - network errors handled uniformly
        healthy = requests.get(url, timeout=5).status_code == 200
    except Exception:
        healthy = False

    path = db_path or DB_PATH
    with sqlite3.connect(path) as conn:
        _ensure_table(conn)
        conn.execute(
            "INSERT INTO service_uptime(service, status) VALUES(?, ?)",
            (name, "up" if healthy else "down"),
        )
        conn.commit()

    if not healthy:
        trigger_alert(f"{name} service unreachable", "critical")
    return healthy


def run_health_checks(*, db_path: Optional[Path] = None) -> Dict[str, bool]:
    """Check default ``SERVICES`` and return their status map."""

    return {
        name: check_service(name, url, db_path=db_path)
        for name, url in SERVICES.items()
    }


__all__ = ["check_service", "run_health_checks", "SERVICES"]

