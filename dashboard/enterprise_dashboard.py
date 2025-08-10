"""Enterprise dashboard routes and utilities."""

from pathlib import Path
import sqlite3
from typing import Any, Callable, Dict, List

from monitoring import BaselineAnomalyDetector

try:  # pragma: no cover - Flask is optional for tests
    from flask import jsonify, render_template
except Exception:  # pragma: no cover - provide fallbacks
    def jsonify(obj: Any) -> Any:  # type: ignore[override]
        return obj

    def render_template(*args: Any, **kwargs: Any) -> str:  # type: ignore[override]
        return ""

try:  # pragma: no cover - dashboard features are optional in tests
    from .integrated_dashboard import (
        app,
        _dashboard as dashboard_bp,
        create_app,
        _load_metrics,
        get_rollback_logs,
        _load_sync_events,
        METRICS_FILE as _METRICS_FILE,
    )
except Exception:  # pragma: no cover - provide fallbacks
    class _DummyApp:
        view_functions: Dict[str, Callable[..., Any]] = {}

        def route(self, *args: Any, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
            def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
                return func

            return decorator

    app = _DummyApp()
    dashboard_bp = app  # type: ignore[assignment]

    def create_app(*args: Any, **kwargs: Any) -> Any:  # type: ignore[override]
        return app

    def _load_metrics() -> Dict[str, Any]:  # type: ignore[override]
        return {}

    def get_rollback_logs() -> List[Dict[str, Any]]:  # type: ignore[override]
        return []

    def _load_sync_events() -> List[Dict[str, Any]]:  # type: ignore[override]
        return []

    _METRICS_FILE = Path("metrics.json")
try:  # pragma: no cover - optional dependency
    from unified_monitoring_optimization_system import get_anomaly_summary
except Exception:  # pragma: no cover
    def get_anomaly_summary(*args: Any, **kwargs: Any) -> Dict[str, Any]:  # type: ignore[override]
        return {}
try:  # pragma: no cover - optional dependency
    from scripts.compliance.update_compliance_metrics import (
        update_compliance_metrics,
        fetch_recent_compliance,
    )
except Exception:  # pragma: no cover
    def update_compliance_metrics(*args: Any, **kwargs: Any) -> None:  # type: ignore[override]
        return None

    def fetch_recent_compliance(*args: Any, **kwargs: Any) -> Dict[str, Any]:  # type: ignore[override]
        return {}

ANALYTICS_DB = Path("databases/analytics.db")
MONITORING_DB = Path("databases/monitoring.db")
METRICS_FILE = _METRICS_FILE


def anomaly_metrics(monitoring_db: Path = MONITORING_DB) -> Dict[str, float]:
    """Return anomaly count and threshold from ``monitoring.db``."""

    detector = BaselineAnomalyDetector(db_path=monitoring_db)
    zscores = detector.zscores()
    anomalies = detector.detect()
    avg_score = float(sum(abs(z) for z in zscores) / len(zscores)) if zscores else 0.0
    return {
        "count": int(sum(anomalies)),
        "avg_anomaly_score": avg_score,
        "threshold": detector.threshold,
    }


def session_lifecycle_stats(db_path: Path = ANALYTICS_DB) -> Dict[str, float]:
    """Aggregate session lifecycle statistics for dashboard display."""

    stats = {
        "count": 0,
        "avg_duration": 0.0,
        "success_rate": 0.0,
        "last_duration": 0.0,
        "last_status": "",
        "last_zero_byte_violations": 0,
    }
    if db_path.exists():
        with sqlite3.connect(db_path) as conn:
            cur = conn.execute(
                "SELECT COUNT(*), AVG(duration_seconds), SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) FROM session_lifecycle",
            )
            count, avg, success = cur.fetchone()
            stats["count"] = int(count or 0)
            stats["avg_duration"] = float(avg or 0.0)
            stats["success_rate"] = (
                float(success or 0) / stats["count"] if stats["count"] else 0.0
            )
            cur = conn.execute(
                "SELECT duration_seconds, status, zero_byte_violations FROM session_lifecycle ORDER BY end_ts DESC LIMIT 1",
            )
            row = cur.fetchone()
            if row:
                stats["last_duration"] = float(row[0] or 0.0)
                stats["last_status"] = row[1] or ""
                stats["last_zero_byte_violations"] = int(row[2] or 0)
    return stats


def load_code_quality_metrics(db_path: Path = ANALYTICS_DB) -> Dict[str, float]:
    """Return latest code quality metrics from analytics.db."""

    metrics = {
        "lint_score": 0.0,
        "test_score": 0.0,
        "placeholder_score": 0.0,
        "composite_score": 0.0,
    }
    if db_path.exists():
        with sqlite3.connect(db_path) as conn:
            row = conn.execute(
                "SELECT lint_score, test_score, placeholder_score, composite_score "
                "FROM code_quality_metrics ORDER BY id DESC LIMIT 1"
            ).fetchone()
            if row:
                metrics["lint_score"] = float(row[0])
                metrics["test_score"] = float(row[1])
                metrics["placeholder_score"] = float(row[2])
                metrics["composite_score"] = float(row[3])
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


def _load_placeholder_history(limit: int = 50) -> List[Dict[str, Any]]:
    """Return placeholder snapshot history."""

    rows: List[Dict[str, Any]] = []
    if ANALYTICS_DB.exists():
        with sqlite3.connect(ANALYTICS_DB) as conn:
            try:
                cur = conn.execute(
                    "SELECT timestamp, open_count, resolved_count "
                    "FROM placeholder_audit_snapshots ORDER BY timestamp LIMIT ?",
                    (limit,),
                )
                rows = [
                    {
                        "timestamp": int(r[0]),
                        "open": int(r[1]),
                        "resolved": int(r[2]),
                    }
                    for r in cur.fetchall()
                ]
            except sqlite3.Error:
                pass
    return rows


def _load_placeholder_details(limit: int = 50) -> Dict[str, List[Dict[str, Any]]]:
    """Return placeholder snapshot history and unresolved placeholders."""

    history: List[Dict[str, Any]] = _load_placeholder_history(limit)
    unresolved: List[Dict[str, Any]] = []
    if ANALYTICS_DB.exists():
        with sqlite3.connect(ANALYTICS_DB) as conn:
            cur = conn.execute(
                "SELECT file_path, line_number FROM placeholder_tasks WHERE status='open' ORDER BY file_path LIMIT ?",
                (limit,),
            )
            unresolved = [
                {"file": r[0], "line": int(r[1])} for r in cur.fetchall()
            ]
    return {"history": history, "unresolved": unresolved}


@app.route("/api/placeholder_details")
def placeholder_details() -> Any:
    """Expose placeholder history and unresolved entries."""

    return jsonify(_load_placeholder_details())


@app.route("/api/placeholder_history")
def placeholder_history() -> Any:
    """Expose placeholder snapshot history."""

    return jsonify({"history": _load_placeholder_history()})


def index() -> str:
    """Render main dashboard with recent corrections."""
    return render_template(
        "dashboard.html",
        metrics=_load_metrics(),
        rollbacks=get_rollback_logs(),
        sync_events=_load_sync_events(),
        audit_results=_load_audit_results(),
        corrections=_load_corrections(),
        anomaly=anomaly_metrics(),
        lifecycle=session_lifecycle_stats(),
        code_quality=load_code_quality_metrics(),
    )


@app.route("/api/refresh_compliance", methods=["POST"])  # trigger composite score recompute
def refresh_compliance() -> Any:  # pragma: no cover
    score = update_compliance_metrics()
    return jsonify({"status": "ok", "composite_score": round(score, 2)})


@app.route("/api/compliance_scores")
def compliance_scores() -> Any:  # pragma: no cover
    rows = fetch_recent_compliance(limit=20)
    return jsonify({"scores": rows})


@app.route("/api/code_quality_metrics")
def code_quality_metrics() -> Any:
    """Expose latest code quality metrics."""
    return jsonify(load_code_quality_metrics())


app.view_functions["dashboard.index"] = index
__all__ = [
    "app",
    "dashboard_bp",
    "create_app",
    "anomaly_metrics",
    "session_lifecycle_stats",
    "_load_corrections",
    "load_code_quality_metrics",
]

