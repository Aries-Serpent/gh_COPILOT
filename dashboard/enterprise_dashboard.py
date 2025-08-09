"""Enterprise dashboard routes and utilities."""

from pathlib import Path
import sqlite3
from typing import Any, Dict, List

from flask import jsonify, render_template

from .integrated_dashboard import (
    app,
    _dashboard as dashboard_bp,
    create_app,
    _load_metrics,
    get_rollback_logs,
    _load_sync_events,
    METRICS_FILE as _METRICS_FILE,
)
from unified_monitoring_optimization_system import get_anomaly_summary
from scripts.compliance.update_compliance_metrics import (
    update_compliance_metrics,
    fetch_recent_compliance,
)

ANALYTICS_DB = Path("databases/analytics.db")
METRICS_FILE = _METRICS_FILE


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


@app.route("/anomalies")
def anomalies() -> Dict[str, list]:
    """Expose recent anomaly summaries."""

    return {"anomalies": get_anomaly_summary(db_path=ANALYTICS_DB)}


def _load_corrections(limit: int = 10) -> List[Dict[str, Any]]:
    """Return recent correction log entries."""
    rows: List[Dict[str, Any]] = []
    if ANALYTICS_DB.exists():
        with sqlite3.connect(ANALYTICS_DB) as conn:
            cur = conn.execute(
                "SELECT timestamp, path, status FROM correction_logs ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            )
            rows = [
                {"timestamp": r[0], "path": r[1], "status": r[2]}
                for r in cur.fetchall()
            ]
    return rows


def _load_audit_results(limit: int = 50) -> List[Dict[str, Any]]:
    """Load audit results directly from analytics.db."""
    rows: List[Dict[str, Any]] = []
    if ANALYTICS_DB.exists():
        with sqlite3.connect(ANALYTICS_DB) as conn:
            cur = conn.execute(
                "SELECT placeholder_type, COUNT(*) FROM todo_fixme_tracking WHERE status='open' "
                "GROUP BY placeholder_type ORDER BY COUNT(*) DESC LIMIT ?",
                (limit,),
            )
            rows = [
                {"placeholder_type": r[0], "count": r[1]} for r in cur.fetchall()
            ]
    return rows


def corrections() -> Any:
    """Expose recent correction log entries."""
    return jsonify(_load_corrections())


app.view_functions["dashboard.get_corrections"] = corrections


@app.route("/sync_events")
def sync_events() -> Any:
    """Compatibility alias for sync-events route."""
    return jsonify(_load_sync_events())


@app.route("/audit_results")
def audit_results_alias() -> Any:
    """Compatibility alias for audit-results route."""
    return jsonify(_load_audit_results())


app.view_functions["dashboard.audit_results"] = audit_results_alias


def index() -> str:
    """Render main dashboard with recent corrections."""
    return render_template(
        "dashboard.html",
        metrics=_load_metrics(),
        rollbacks=get_rollback_logs(),
        sync_events=_load_sync_events(),
        audit_results=_load_audit_results(),
        corrections=_load_corrections(),
    )


@app.route("/api/refresh_compliance", methods=["POST"])  # trigger composite score recompute
def refresh_compliance() -> Any:  # pragma: no cover
    score = update_compliance_metrics()
    return jsonify({"status": "ok", "composite_score": round(score, 2)})


@app.route("/api/compliance_scores")
def compliance_scores() -> Any:  # pragma: no cover
    rows = fetch_recent_compliance(limit=20)
    return jsonify({"scores": rows})


app.view_functions["dashboard.index"] = index
__all__ = ["app", "dashboard_bp", "create_app", "anomaly_metrics", "_load_corrections"]
