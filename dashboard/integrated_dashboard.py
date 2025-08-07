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
    calculate_composite_score,
    get_latest_compliance_score,
)
from utils.validation_utils import calculate_composite_compliance_score

# Paths and database locations
METRICS_FILE = Path(__file__).with_name("metrics.json")
METRICS_PATH = METRICS_FILE  # Backward compatibility
CORRECTIONS_DIR = Path("dashboard/compliance")
ANALYTICS_DB = Path("databases/analytics.db")


# Blueprint definition
_dashboard = Blueprint(
    "dashboard",
    __name__,
    template_folder=str(Path(__file__).parent / "templates"),
    static_folder=str(Path(__file__).parent / "static"),
)


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
                        score, breakdown = calculate_composite_score(
                            row["ruff_issues"],
                            row["tests_passed"],
                            row["tests_failed"],
                            row["placeholders_open"],
                            row["placeholders_resolved"],
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
        except sqlite3.Error:
            pass
    return metrics


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
    return render_template(
        "dashboard.html",
        metrics=_load_metrics(),
        rollbacks=get_rollback_logs(),
    )


@_dashboard.get("/metrics")
def metrics() -> Any:
    return jsonify(_load_metrics())


@_dashboard.get("/metrics_stream")
def metrics_stream() -> Response:
    once = request.args.get("once") == "1"
    interval = int(request.args.get("interval", "5"))

    def generate() -> Any:
        while True:
            payload = json.dumps(_load_metrics())
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


@_dashboard.get("/placeholder-audit")
def get_placeholder_audit() -> Any:
    entries: list[dict[str, Any]] = []
    if ANALYTICS_DB.exists():
        with sqlite3.connect(ANALYTICS_DB) as conn:
            try:
                cur = conn.execute(
                    "SELECT file_path, line_number, placeholder_type, context FROM placeholder_audit ORDER BY id DESC LIMIT 100",
                )
                entries = [
                    {
                        "file_path": row[0],
                        "line_number": row[1],
                        "placeholder_type": row[2],
                        "context": row[3],
                    }
                    for row in cur.fetchall()
                ]
            except sqlite3.Error:
                pass
    return jsonify({"results": entries})


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
    return render_template("rollback_logs.html", logs=get_rollback_logs())


@_dashboard.get("/audit-results/view")
def audit_results_view() -> str:
    return render_template("audit_results.html", results=_load_audit_results())


@_dashboard.get("/sync-events/view")
def sync_events_view() -> str:
    return render_template("sync_events.html", events=_load_sync_events())


@_dashboard.get("/dashboard/compliance")
def dashboard_compliance() -> Any:
    return jsonify({"metrics": _load_metrics(), "rollbacks": get_rollback_logs()})


@_dashboard.get("/dashboard/rollback")
def dashboard_rollback() -> str:
    return render_template("rollback_logs.html", logs=get_rollback_logs())


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).parent / "templates"),
        static_folder=str(Path(__file__).parent / "static"),
    )
    app.register_blueprint(_dashboard)
    return app


app = create_app()

__all__ = ["app", "create_app", "_dashboard"]
