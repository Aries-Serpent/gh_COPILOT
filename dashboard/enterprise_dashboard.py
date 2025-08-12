"""Enterprise dashboard routes and utilities."""

import json
import time
from pathlib import Path
import sqlite3
import threading
import asyncio
from typing import Any, Callable, Dict, List
import queue

from monitoring import BaselineAnomalyDetector
from enterprise_modules.compliance import validate_enterprise_operation

try:  # pragma: no cover - Flask is optional for tests
    from flask import jsonify, render_template, Response, request
except Exception:  # pragma: no cover - provide fallbacks

    def jsonify(obj: Any) -> Any:  # type: ignore[override]
        return obj

    def render_template(*args: Any, **kwargs: Any) -> str:  # type: ignore[override]
        return ""

    def Response(*args: Any, **kwargs: Any) -> Any:  # type: ignore[override]
        return None

    class _Request:
        args: Dict[str, Any] = {}
        environ: Dict[str, Any] = {}

    request = _Request()  # type: ignore[assignment]


try:  # pragma: no cover - dashboard features are optional in tests
    from typing import Any, cast

    from .integrated_dashboard import (
        app,
        _dashboard as dashboard_bp,
        create_app,
        _load_metrics as _real_load_metrics,
        get_rollback_logs as _real_get_rollback_logs,
        _load_sync_events as _real_load_sync_events,
        METRICS_FILE as _METRICS_FILE,
    )
    _load_metrics = cast(Any, _real_load_metrics)
    get_rollback_logs = cast(Any, _real_get_rollback_logs)
    _load_sync_events = cast(Any, _real_load_sync_events)
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

    def _load_metrics(*args: Any, **kwargs: Any):  # type: ignore[override]
        return {}

    def get_rollback_logs(*args: Any, **kwargs: Any):  # type: ignore[override]
        return []

    def _load_sync_events(*args: Any, **kwargs: Any):  # type: ignore[override]
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

    def update_compliance_metrics(*args: Any, **kwargs: Any) -> float:  # type: ignore[override]
        return 0.0

    def fetch_recent_compliance(*args: Any, **kwargs: Any) -> List[Dict[str, float]]:  # type: ignore[override]
        return []


ANALYTICS_DB = Path("databases/analytics.db")
MONITORING_DB = Path("databases/monitoring.db")
METRICS_FILE = _METRICS_FILE
CORRECTIONS_WS_PORT = 8767


def _load_metrics_with_file() -> Dict[str, Any]:
    """Wrapper ensuring ``_load_metrics`` uses the local ``METRICS_FILE``."""
    try:
        _load_metrics.__globals__["METRICS_FILE"] = METRICS_FILE
    except Exception:
        pass
    return _load_metrics()


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
            stats["success_rate"] = float(success or 0) / stats["count"] if stats["count"] else 0.0
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


@app.route("/dashboard/compliance")
def dashboard_compliance() -> str:
    """Render compliance metrics from analytics.db."""
    placeholder_count = 0
    last_resolved = ""
    audit_logs: List[Dict[str, Any]] = []
    if ANALYTICS_DB.exists():
        validate_enterprise_operation(str(ANALYTICS_DB))
        with sqlite3.connect(ANALYTICS_DB) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS todo_fixme_tracking (status TEXT, resolved_timestamp TEXT)"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS code_audit_log (summary TEXT, ts TEXT)"
            )
            cur = conn.execute(
                "SELECT COUNT(*), MAX(resolved_timestamp) FROM todo_fixme_tracking WHERE status='open'"
            )
            count, ts = cur.fetchone()
            placeholder_count = int(count or 0)
            last_resolved = ts or ""
            audit_logs = [
                {"ts": r[0], "summary": r[1]}
                for r in conn.execute(
                    "SELECT ts, summary FROM code_audit_log ORDER BY ts DESC LIMIT 10"
                ).fetchall()
            ]
    return render_template(
        "compliance.html",
        placeholders=placeholder_count,
        last_resolved=last_resolved,
        audit_logs=audit_logs,
    )


@app.route("/anomalies")
def anomalies() -> Dict[str, Any]:
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
            rows = [{"timestamp": r[0], "path": r[1], "status": r[2]} for r in cur.fetchall()]
    return rows


_sse_subscribers: list["queue.Queue[str]"] = []
_ws_clients: list[Any] = []
_last_corrections_payload = ""
_broadcast_thread_started = False


def _broadcast_corrections(payload: str | None = None) -> None:
    """Broadcast ``payload`` to SSE and WebSocket clients."""
    global _last_corrections_payload
    if payload is None:
        payload = json.dumps(_load_corrections())
    if payload == _last_corrections_payload:
        return
    _last_corrections_payload = payload
    for q in list(_sse_subscribers):
        try:
            q.put_nowait(payload)
        except Exception:
            _sse_subscribers.remove(q)
    for ws in list(_ws_clients):
        try:
            ws.send(payload)
        except Exception:
            _ws_clients.remove(ws)


def _corrections_broadcast_loop(interval: int = 5) -> None:
    """Periodically load corrections and broadcast to subscribers."""
    while True:
        _broadcast_corrections()
        time.sleep(interval)


def _ensure_corrections_thread() -> None:
    """Start the corrections broadcast thread if not already running."""
    global _broadcast_thread_started
    if not _broadcast_thread_started:
        threading.Thread(target=_corrections_broadcast_loop, daemon=True).start()
        _broadcast_thread_started = True


def _load_audit_results(limit: int = 50) -> List[Dict[str, Any]]:
    """Load audit results directly from analytics.db."""
    rows: List[Dict[str, Any]] = []
    if ANALYTICS_DB.exists():
        with sqlite3.connect(ANALYTICS_DB) as conn:
            cur = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='placeholder_audit'"
            )
            table_exists = cur.fetchone() is not None
            if table_exists:
                cur = conn.execute(
                    "SELECT placeholder_type, COUNT(*) FROM placeholder_audit "
                    "GROUP BY placeholder_type ORDER BY COUNT(*) DESC LIMIT ?",
                    (limit,),
                )
            else:
                cur = conn.execute(
                    "SELECT placeholder_type, COUNT(*) FROM todo_fixme_tracking WHERE status='open' "
                    "GROUP BY placeholder_type ORDER BY COUNT(*) DESC LIMIT ?",
                    (limit,),
                )
            rows = [{"placeholder_type": r[0], "count": r[1]} for r in cur.fetchall()]
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


@app.route("/metrics")
def metrics() -> Any:
    """Expose metrics and placeholder history."""
    return jsonify({"metrics": _load_metrics_with_file(), "placeholder_history": _load_placeholder_history()})


@app.route("/metrics_stream")
def metrics_stream() -> Response:
    """Stream live metrics updates via SSE."""
    once = request.args.get("once") == "1"
    interval = int(request.args.get("interval", "5"))

    def generate() -> Any:
        while True:
            metrics = _load_metrics_with_file()
            metrics["placeholder_history"] = _load_placeholder_history()
            yield f"data: {json.dumps(metrics)}\n\n"
            if once:
                break
            time.sleep(interval)

    return Response(generate(), mimetype="text/event-stream")


@app.route("/corrections_stream")
def corrections_stream() -> Response:
    """Stream recent correction logs via SSE."""
    once = request.args.get("once") == "1"
    if once:
        payload = json.dumps(_load_corrections())
        def generate_once() -> Any:
            yield f"data: {payload}\n\n"
        return Response(generate_once(), mimetype="text/event-stream")

    def generate() -> Any:
        q: "queue.Queue[str]" = queue.Queue()
        _sse_subscribers.append(q)
        _ensure_corrections_thread()
        try:
            while True:
                data = q.get()
                yield f"data: {data}\n\n"
        finally:
            _sse_subscribers.remove(q)

    return Response(generate(), mimetype="text/event-stream")


@app.route("/ws/corrections")
def corrections_ws() -> Any:
    """WebSocket endpoint for correction broadcasts with SSE fallback."""
    ws = request.environ.get("wsgi.websocket")
    if ws is None:
        return corrections_stream()
    _ws_clients.append(ws)
    _ensure_corrections_thread()
    try:
        while True:
            if ws.receive() is None:
                break
    finally:
        if ws in _ws_clients:
            _ws_clients.remove(ws)
    return ""


app.view_functions["dashboard.metrics"] = metrics
app.view_functions["dashboard.metrics_stream"] = metrics_stream
app.view_functions["dashboard.corrections_stream"] = corrections_stream
app.view_functions["dashboard.corrections_ws"] = corrections_ws


def _load_placeholder_history(limit: int = 50) -> List[Dict[str, Any]]:
    """Return placeholder snapshot history."""

    rows: List[Dict[str, Any]] = []
    if ANALYTICS_DB.exists():
        with sqlite3.connect(ANALYTICS_DB) as conn:
            try:
                cur = conn.execute(
                    "SELECT timestamp, open_count, resolved_count "
                    "FROM placeholder_audit_snapshots ORDER BY timestamp DESC LIMIT ?",
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
                rows.reverse()
            except sqlite3.Error:
                pass
    return rows


def _load_placeholder_audit(limit: int = 50) -> Dict[str, Any]:
    """Return placeholder trend history, totals and unresolved placeholders."""

    history: List[Dict[str, Any]] = _load_placeholder_history(limit)
    totals = {
        "open": history[-1]["open"] if history else 0,
        "resolved": history[-1]["resolved"] if history else 0,
    }
    unresolved: List[Dict[str, Any]] = []
    if ANALYTICS_DB.exists():
        with sqlite3.connect(ANALYTICS_DB) as conn:
            try:
                cur = conn.execute(
                    "SELECT file_path, line_number, placeholder_type, context FROM placeholder_audit ORDER BY id DESC LIMIT ?",
                    (limit,),
                )
                unresolved = [
                    {
                        "file": row[0],
                        "line": int(row[1]),
                        "type": row[2],
                        "context": row[3],
                    }
                    for row in cur.fetchall()
                ]
            except sqlite3.Error:
                pass
    return {"history": history, "totals": totals, "unresolved": unresolved}


@app.route("/api/placeholder_audit")
def placeholder_audit() -> Any:
    """Expose placeholder history and unresolved entries."""

    return jsonify(_load_placeholder_audit())


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
    return jsonify({"status": "ok", "composite_score": round(score or 0.0, 2)})


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
    "CORRECTIONS_WS_PORT",
]
