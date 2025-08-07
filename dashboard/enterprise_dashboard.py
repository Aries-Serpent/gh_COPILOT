"""Enterprise dashboard routes and utilities."""

from pathlib import Path
import sqlite3
from typing import Any, Dict

from flask import jsonify

from .integrated_dashboard import app, _dashboard as dashboard_bp, create_app
from unified_monitoring_optimization_system import get_anomaly_summary

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


def compliance_metrics(limit: int = 10, db_path: Path | None = None) -> Dict[str, Any]:
    """Return latest compliance score and recent trend data."""

    db = db_path or ANALYTICS_DB
    results: Dict[str, Any] = {"latest": None, "trend": []}
    if db.exists():
        with sqlite3.connect(db) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                """
                SELECT timestamp, composite_score, lint_score, test_score, placeholder_score
                FROM compliance_scores
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = cur.fetchall()
            trend = [
                {
                    "timestamp": row["timestamp"],
                    "composite_score": row["composite_score"],
                    "breakdown": {
                        "lint_score": row["lint_score"],
                        "test_score": row["test_score"],
                        "placeholder_score": row["placeholder_score"],
                    },
                }
                for row in rows
            ]
            if trend:
                results["latest"] = trend[0]
            results["trend"] = trend
    return results


@app.route("/anomalies")
def anomalies() -> Dict[str, list]:
    """Expose recent anomaly summaries."""

    return {"anomalies": get_anomaly_summary(db_path=ANALYTICS_DB)}


@app.route("/compliance-metrics")
def get_compliance_metrics() -> Any:
    """Expose compliance score breakdown and trend."""

    return jsonify(compliance_metrics())


__all__ = [
    "app",
    "dashboard_bp",
    "create_app",
    "anomaly_metrics",
    "compliance_metrics",
]
