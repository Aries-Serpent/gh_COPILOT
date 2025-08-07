"""Enterprise dashboard routes and utilities."""

from pathlib import Path
import sqlite3
from typing import Any, Dict

from flask import jsonify

from .integrated_dashboard import (
    app,
    _dashboard as dashboard_bp,
    _load_audit_results,
    _load_sync_events,
    create_app,
)

ANALYTICS_DB = Path("databases/analytics.db")


def anomaly_metrics(db_path: Path = ANALYTICS_DB) -> Dict[str, float]:
    """Return aggregate anomaly metrics for dashboard display."""

    metrics = {"count": 0, "avg_anomaly_score": 0.0}
    if db_path.exists():
        with sqlite3.connect(db_path) as conn:
            cur = conn.execute(
                "SELECT COUNT(*), AVG(anomaly_score) FROM anomaly_results",
            )
            count, avg = cur.fetchone()
            metrics["count"] = int(count or 0)
            metrics["avg_anomaly_score"] = float(avg or 0.0)
    return metrics


@app.get("/sync_events")
def sync_events() -> Any:
    """Return recent synchronization events."""
    return jsonify(_load_sync_events())


@app.get("/audit_results")
def audit_results() -> Any:
    """Return placeholder audit aggregation results."""
    return jsonify(_load_audit_results())


__all__ = ["app", "dashboard_bp", "create_app", "anomaly_metrics"]

