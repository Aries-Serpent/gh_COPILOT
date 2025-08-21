from __future__ import annotations

import json
import logging
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from flask import (
    Blueprint,
    Flask,
    Response,
    jsonify,
    render_template,
    request,
)
from tqdm import tqdm

from scripts.correction_logger_and_rollback import CorrectionLoggerRollback
from database_first_synchronization_engine import list_events
from enterprise_modules.compliance import (
    calculate_compliance_score,
    get_latest_compliance_score,
    validate_enterprise_operation,
)
from utils.validation_utils import calculate_composite_compliance_score
from web_gui import middleware, security
from web_gui.certificates import init_app as init_certificates

try:  # optional quantum dashboard metrics
    from web_gui.dashboards.quantum_dashboard import (
        get_metrics as get_quantum_metrics,
    )
except Exception:  # pragma: no cover - gracefully degrade if unavailable
    def get_quantum_metrics() -> dict[str, float]:
        return {}

# Paths and database locations
METRICS_FILE = Path(__file__).with_name("metrics.json")
METRICS_PATH = METRICS_FILE  # Backward compatibility
CORRECTIONS_DIR = Path("dashboard/compliance")
ANALYTICS_DB = Path("databases/analytics.db")
THRESHOLDS_FILE = Path(__file__).resolve().parents[1] / "thresholds.json"


# Blueprint definition
_dashboard = Blueprint(
    "dashboard",
    __name__,
    template_folder=str(Path(__file__).parent / "templates"),
    static_folder=str(Path(__file__).parent / "static"),
)


def _load_thresholds() -> dict[str, dict[str, float]]:
    """Load metric threshold configuration if available.

    Falls back to the legacy path under ``dashboard/`` if the new root-level
    configuration is missing.  Both locations use the same JSON structure.
    """
    for path in (THRESHOLDS_FILE, Path(__file__).with_name("thresholds.json")):
        if path.exists():
            try:
                return json.loads(path.read_text())
            except json.JSONDecodeError:
                logging.error("Thresholds decode error", exc_info=True)
    return {}


def _compute_alert(value: float, bounds: dict[str, float]) -> str:
    """Return alert level for *value* based on *bounds* mapping."""
    warning = bounds.get("warning")
    critical = bounds.get("critical")
    if critical is not None and value < critical:
        return "critical"
    if warning is not None and value < warning:
        return "warning"
    return "ok"


def _load_metrics() -> dict[str, Any]:
    """Load combined metrics from metrics.json and analytics.db."""
    metrics: dict[str, Any] = {
        "placeholder_removal": 0,
        "compliance_score": 0.0,
        "violation_count": 0,
        "rollback_count": 0,
        "timestamp": datetime.utcnow().isoformat(),
        "score": 0.0,
        "last_audit_date": None,
        "latest_anomaly_score": 0.0,
        "latest_anomaly_composite": 0.0,
        "latest_quantum_score": 0.0,
    }
    if METRICS_FILE.exists():
        try:
            metrics.update(json.loads(METRICS_FILE.read_text()).get("metrics", {}))
        except json.JSONDecodeError:
            logging.error("Metrics decode error", exc_info=True)
    if ANALYTICS_DB.exists():
        try:
            metrics["compliance_score"] = get_latest_compliance_score(ANALYTICS_DB)
        except sqlite3.Error:
            pass
        try:
            with sqlite3.connect(ANALYTICS_DB) as conn:
                conn.row_factory = sqlite3.Row
                try:
                    cur = conn.execute(
                        """
                        SELECT ruff_issues, tests_passed, tests_failed,
                               placeholders_open, placeholders_resolved, composite_score, ts
                        FROM code_quality_metrics
                        ORDER BY id DESC LIMIT 1
                        """,
                    )
                    row = cur.fetchone()
                    if row:
                        score, breakdown = calculate_compliance_score(
                            row["ruff_issues"],
                            row["tests_passed"],
                            row["tests_failed"],
                            row["placeholders_open"],
                            row["placeholders_resolved"],
                            0,
                            0,
                        )
                        metrics["code_quality_score"] = score
                        metrics["composite_score"] = score
                        metrics["score_breakdown"] = breakdown
                        metrics["last_audit_date"] = row["ts"]
                except sqlite3.Error:
                    try:
                        cur = conn.execute(
                            """
                            SELECT ruff_issues, tests_passed, tests_failed,
                                   placeholders, composite_score, ts
                            FROM code_quality_metrics
                            ORDER BY id DESC LIMIT 1
                            """,
                        )
                        row = cur.fetchone()
                        if row:
                            scores = calculate_composite_compliance_score(
                                row["ruff_issues"],
                                row["tests_passed"],
                                row["tests_failed"],
                                row["placeholders"],
                                0,
                            )
                            metrics["compliance_score"] = scores["composite"]
                            metrics["composite_score"] = row["composite_score"]
                            metrics["last_audit_date"] = row["ts"]
                    except sqlite3.Error:
                        pass
                try:
                    cur = conn.execute(
                        "SELECT anomaly_score, quantum_score, composite_score FROM anomaly_results ORDER BY id DESC LIMIT 1"
                    )
                    row = cur.fetchone()
                    if row:
                        metrics["latest_anomaly_score"] = row[0]
                        if row[1] is not None:
                            metrics["latest_quantum_score"] = row[1]
                        metrics["latest_anomaly_composite"] = row[2]
                except sqlite3.Error:
                    pass
                try:
                    cur = conn.execute(
                        "SELECT score FROM quantum_scores ORDER BY id DESC LIMIT 1"
                    )
                    row = cur.fetchone()
                    if row:
                        metrics["latest_quantum_score"] = row[0]
                except sqlite3.Error:
                    pass
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM placeholder_audit")
                metrics["violation_count"] = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM rollback_logs")
                metrics["rollback_count"] = cur.fetchone()[0]
                try:
                    cur = conn.execute(
                        "SELECT open_count, resolved_count FROM placeholder_audit_snapshots ORDER BY id DESC LIMIT 1"
                    )
                    row = cur.fetchone()
                    if row:
                        metrics["open_placeholders"] = row[0]
                        metrics["resolved_placeholders"] = row[1]
                except sqlite3.Error:
                    pass
        except sqlite3.Error:
            pass
    thresholds = _load_thresholds()
    alerts: dict[str, str] = {}
    for name, bounds in thresholds.items():
        value = metrics.get(name)
        if isinstance(value, (int, float)):
            alerts[name] = _compute_alert(float(value), bounds)
    metrics["alerts"] = alerts
    metrics["thresholds"] = thresholds
    return metrics


def _load_placeholder_history(limit: int = 30) -> list[dict[str, Any]]:
    """Return historical open placeholder counts."""
    rows: list[dict[str, Any]] = []
    if not ANALYTICS_DB.exists():
        return rows
    try:
        with sqlite3.connect(ANALYTICS_DB) as conn:
            cur = conn.execute(
                "SELECT DATE(timestamp, 'unixepoch') as day, open_count FROM placeholder_audit_snapshots ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            )
            rows = [{"date": r[0], "count": r[1]} for r in cur.fetchall()][::-1]
    except sqlite3.Error:
        pass
    return rows


def get_rollback_logs(limit: int = 10) -> list[dict[str, Any]]:
    """Return recent rollback log entries."""
    records: list[dict[str, Any]] = []
    if not ANALYTICS_DB.exists():
        return records
    try:
        with sqlite3.connect(ANALYTICS_DB) as conn:
            cur = conn.execute(
                "SELECT timestamp, target, backup FROM rollback_logs ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            )
            records = [
                {"timestamp": row[0], "target": row[1], "backup": row[2]}
                for row in cur.fetchall()
            ]
    except sqlite3.Error:
        pass
    return records


def _load_compliance_payload() -> dict[str, Any]:
    """Aggregate compliance metrics, placeholder counts, and audit log entries."""
    payload: dict[str, Any] = {
        "metrics": _load_metrics(),
        "rollbacks": get_rollback_logs(),
        "placeholders_open": 0,
        "audit_log": [],
        "audit_count": 0,
        "last_resolved": "",
        "todo_entries": [],
    }
    if ANALYTICS_DB.exists():
        try:
            validate_enterprise_operation(str(ANALYTICS_DB))
            with sqlite3.connect(ANALYTICS_DB) as conn:
                cur = conn.execute(
                    "SELECT COUNT(*), MAX(resolved_timestamp) FROM todo_fixme_tracking WHERE status='open'"
                )
                count, ts = cur.fetchone()
                payload["placeholders_open"] = int(count or 0)
                payload["last_resolved"] = ts or ""
                cur = conn.execute(
                    "SELECT file_path, line_number, placeholder_type FROM todo_fixme_tracking WHERE status='open' LIMIT 20"
                )
                payload["todo_entries"] = [
                    {"file_path": r[0], "line_number": r[1], "placeholder_type": r[2]}
                    for r in cur.fetchall()
                ]
                cur = conn.execute(
                    "SELECT ts, summary FROM code_audit_log ORDER BY ts DESC LIMIT 10"
                )
                rows = cur.fetchall()
                payload["audit_log"] = [
                    {"ts": row[0], "summary": row[1]} for row in rows
                ]
                payload["audit_count"] = len(rows)
        except sqlite3.Error:
            pass
    return payload


# Alias for external imports
_compliance_payload = _load_compliance_payload

def _load_sync_events(limit: int = 10) -> list[dict[str, Any]]:
    try:
        return list_events(ANALYTICS_DB, limit)
    except sqlite3.Error:
        return []


def _load_audit_results(limit: int = 50) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not ANALYTICS_DB.exists():
        return rows
    try:
        with sqlite3.connect(ANALYTICS_DB) as conn:
            cur = conn.execute(
                "SELECT placeholder_type, COUNT(*) FROM todo_fixme_tracking WHERE status='open' GROUP BY placeholder_type ORDER BY COUNT(*) DESC LIMIT ?",
                (limit,),
            )
            rows = [{"placeholder_type": r[0], "count": r[1]} for r in cur.fetchall()]
    except sqlite3.Error:
        pass
    return rows


def _load_corrections() -> dict[str, Any]:
    summary = CORRECTIONS_DIR / "correction_summary.json"
    if summary.exists():
        try:
            return json.loads(summary.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


@_dashboard.get("/")
def index() -> str:
    compliance = _load_compliance_payload()
    return render_template(
        "dashboard.html",
        metrics=compliance["metrics"],
        rollbacks=compliance["rollbacks"],
        sync_events=_load_sync_events(),
        audit_results=_load_audit_results(),
        compliance=compliance,
    )


@_dashboard.get("/metrics")
def metrics() -> Any:
    return jsonify(
        {
            "metrics": _load_metrics(),
            "placeholder_history": _load_placeholder_history(),
        }
    )


@_dashboard.get("/metrics_stream")
def metrics_stream() -> Response:
    once = request.args.get("once") == "1"
    interval = int(request.args.get("interval", "5"))

    def generate() -> Any:
        while True:
            metrics = _load_metrics()
            metrics["placeholder_history"] = _load_placeholder_history()
            payload = json.dumps(metrics)
            yield f"data: {payload}\n\n"
            if once:
                break
            time.sleep(interval)

    return Response(generate(), mimetype="text/event-stream")


@_dashboard.get("/rollback-logs")
def rollback_logs() -> Any:
    return jsonify(get_rollback_logs())


@_dashboard.get("/audit-results")
def audit_results() -> Any:
    return jsonify(_load_audit_results())


@_dashboard.get("/sync-events")
def sync_events() -> Any:
    return jsonify(_load_sync_events())


@_dashboard.get("/corrections")
def get_corrections() -> Any:
    return jsonify(_load_corrections())


@_dashboard.get("/corrections/view")
def corrections_view() -> Any:
    """Render correction history using HTML template."""
    data = _load_corrections()
    return render_template("corrections.html", corrections=data.get("corrections", []))


@_dashboard.get("/compliance")
def get_compliance() -> Any:
    return jsonify({"metrics": _load_metrics(), "corrections": _load_corrections().get("corrections", [])})


@_dashboard.get("/violations")
def get_violations() -> Any:
    logs: list[dict[str, Any]] = []
    if ANALYTICS_DB.exists():
        with sqlite3.connect(ANALYTICS_DB) as conn:
            cur = conn.cursor()
            cur.execute("SELECT timestamp, details FROM violation_logs ORDER BY timestamp DESC LIMIT 50")
            logs = [dict(timestamp=row[0], details=row[1]) for row in cur.fetchall()]
    return jsonify({"violations": logs})


def _load_placeholder_audit(limit: int = 50) -> dict[str, Any]:
    """Return placeholder trend history, totals, and unresolved entries."""

    history = _load_placeholder_history(limit)
    totals = {
        "open": history[-1]["open"] if history else 0,
        "resolved": history[-1]["resolved"] if history else 0,
    }
    unresolved: list[dict[str, Any]] = []
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


@_dashboard.get("/placeholder-audit")
def get_placeholder_audit() -> Any:
    return jsonify({"results": _load_placeholder_audit()["unresolved"]})


@_dashboard.get("/api/placeholder_audit")
def api_placeholder_audit() -> Any:
    """Expose placeholder audit history and counts for the dashboard."""

    return jsonify(_load_placeholder_audit())


@_dashboard.post("/rollback")
def trigger_rollback() -> Any:
    payload = request.get_json(force=True) or {}
    target = Path(payload.get("target", ""))
    backup = payload.get("backup")
    rollbacker = CorrectionLoggerRollback(ANALYTICS_DB)
    with tqdm(total=1, desc="rollback", unit="step") as bar:
        ok = rollbacker.auto_rollback(target, Path(backup) if backup else None)
        bar.update(1)
    return jsonify({"status": "ok" if ok else "failed"})


@_dashboard.get("/metrics/view")
def metrics_view() -> str:
    return render_template("metrics.html", metrics=_load_metrics())


@_dashboard.get("/rollback-logs/view")
def rollback_logs_view() -> str:
    return render_template("html/rollback_logs.html", logs=get_rollback_logs())


@_dashboard.get("/audit-results/view")
def audit_results_view() -> str:
    return render_template("audit_results.html", results=_load_audit_results())


@_dashboard.get("/sync-events/view")
def sync_events_view() -> str:
    return render_template("sync_events.html", events=_load_sync_events())


@_dashboard.get("/quantum-dashboard")
def quantum_dashboard_view() -> str:
    return render_template("html/quantum_dashboard.html", metrics=get_quantum_metrics())


@_dashboard.get("/dashboard/compliance")
def dashboard_compliance() -> Any:
    return jsonify(_load_compliance_payload())


@_dashboard.get("/dashboard/rollback")
def dashboard_rollback() -> str:
    return render_template("html/rollback_logs.html", logs=get_rollback_logs())


def create_app(config: dict | None = None) -> Flask:
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).parent / "templates"),
        static_folder=str(Path(__file__).parent / "static"),
    )
    app.jinja_loader.searchpath.append(
        str(Path(__file__).resolve().parents[1] / "web_gui" / "templates")
    )

    if config:
        app.config.update(config)

    # Initialize subsystems
    init_certificates(app)
    security.init_app(app)
    middleware.init_app(app)

    app.register_blueprint(_dashboard)
    return app


app = create_app()

__all__ = ["app", "create_app", "_dashboard"]
