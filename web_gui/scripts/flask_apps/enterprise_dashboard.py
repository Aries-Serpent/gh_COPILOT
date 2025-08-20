#!/usr/bin/env python3
"""Enterprise compliance dashboard with real-time metrics."""

from __future__ import annotations

import json
import logging
import sqlite3
import time
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List

from flask import (
    Flask,
    Response,
    jsonify,
    render_template,
    request,
)
from tqdm import tqdm

from dashboard.compliance_metrics_updater import ComplianceMetricsUpdater

from config.secret_manager import get_secret
from utils.cross_platform_paths import CrossPlatformPathManager
from enterprise_modules.compliance import get_latest_compliance_score
from web_gui import middleware
from scripts.correction_logger_and_rollback import CorrectionLoggerRollback

workspace_root = CrossPlatformPathManager.get_workspace_path()
ANALYTICS_DB = Path(os.getenv("ANALYTICS_DB", workspace_root / "databases" / "analytics.db"))
COMPLIANCE_DIR = Path(os.getenv("COMPLIANCE_DIR", workspace_root / "dashboard" / "compliance"))

TEMPLATES = Path(__file__).resolve().parents[2] / "templates"
STATIC = Path(__file__).resolve().parents[2] / "static"
app = Flask(__name__, template_folder=str(TEMPLATES), static_folder=str(STATIC))
app.secret_key = get_secret("FLASK_SECRET_KEY", "dev_key")
middleware.init_app(app)
LOG_FILE = Path("artifacts/logs/dashboard") / "dashboard.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(level=logging.INFO, handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])

# Compliance metrics updater used for live streaming
metrics_updater = ComplianceMetricsUpdater(COMPLIANCE_DIR, test_mode=True)


def _get_lessons_integration_status(cur: sqlite3.Cursor) -> str:
    """Return the latest lessons integration status from the database.

    Provides descriptive fallbacks when the primary table is missing or empty."""
    try:
        cur.execute(
            "SELECT integration_status FROM integration_score_calculations ORDER BY timestamp DESC LIMIT 1"
        )
        row = cur.fetchone()
        if row and row[0]:
            return row[0]
        cur.execute("SELECT COUNT(*) FROM integration_score_calculations")
        if cur.fetchone()[0] == 0:
            logging.info("No integration score records found")
            return "NO_DATA"
    except sqlite3.OperationalError:
        try:
            cur.execute("SELECT COUNT(*) FROM enhanced_lessons_learned")
            return "PENDING" if cur.fetchone()[0] else "NO_DATA"
        except sqlite3.Error as exc:
            logging.error("Lessons integration fallback error: %s", exc)
            return "NO_DATA"
    except sqlite3.Error as exc:
        logging.error("Lessons integration fetch error: %s", exc)
        return "NO_DATA"
    return "UNKNOWN"


def _get_average_query_latency(cur: sqlite3.Cursor) -> float:
    """Return the average query latency from performance metrics."""
    try:
        cur.execute(
            "SELECT AVG(metric_value) FROM performance_metrics WHERE metric_name='query_latency'"
        )
        val = cur.fetchone()[0]
        return float(val) if val is not None else 0.0
    except sqlite3.Error as exc:
        logging.error("Query latency fetch error: %s", exc)
        return 0.0


def _fetch_metrics() -> Dict[str, Any]:
    """Fetch compliance metrics including lessons integration and query latency."""
    metrics: Dict[str, Any] = {
        "total_placeholders": 0,
        "lessons_integration_status": "UNKNOWN",
        "average_query_latency": 0.0,
        "composite_score": 0.0,
        "score_breakdown": {},
    }
    try:  # pragma: no cover - best effort integration with updater
        data = metrics_updater._fetch_compliance_metrics(test_mode=True)
        if isinstance(data, dict):
            metrics.update(data)
    except Exception:
        pass
    try:
        metrics["compliance_score"] = get_latest_compliance_score(ANALYTICS_DB)
    except sqlite3.Error as exc:  # pragma: no cover - fallback on schema issues
        logging.error("Compliance score fetch error: %s", exc)
        metrics["compliance_score"] = 0.0
    if ANALYTICS_DB.exists():
        with sqlite3.connect(ANALYTICS_DB) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            try:
                cur.execute("SELECT COUNT(*) FROM todo_fixme_tracking")
                metrics["total_placeholders"] = cur.fetchone()[0]
                metrics["lessons_integration_status"] = _get_lessons_integration_status(cur)
                metrics["average_query_latency"] = _get_average_query_latency(cur)
                cur.execute(
                    """
                    SELECT ruff_issues, tests_passed, tests_failed,
                           placeholders_open, placeholders_resolved,
                           composite_score
                    FROM code_quality_metrics
                    ORDER BY id DESC LIMIT 1
                    """
                )
                row = cur.fetchone()
                if row and row["composite_score"] is not None:
                    metrics["composite_score"] = row["composite_score"]
                    total_tests = row["tests_passed"] + row["tests_failed"]
                    total_ph = row["placeholders_open"] + row["placeholders_resolved"]
                    metrics["score_breakdown"] = {
                        "ruff_issues": row["ruff_issues"],
                        "tests_passed": row["tests_passed"],
                        "tests_failed": row["tests_failed"],
                        "placeholders_open": row["placeholders_open"],
                        "placeholders_resolved": row["placeholders_resolved"],
                        "test_pass_ratio": row["tests_passed"] / total_tests if total_tests else 0.0,
                        "placeholder_resolution_ratio": row["placeholders_resolved"] / total_ph if total_ph else 1.0,
                    }
            except sqlite3.Error as exc:
                logging.error("Metric fetch error: %s", exc)
    return metrics


def _fetch_rollbacks(limit: int = 5) -> List[Dict[str, Any]]:
    """Fetch recent rollback events directly from ``analytics.db``."""
    records: List[Dict[str, Any]] = []
    if ANALYTICS_DB.exists():
        with sqlite3.connect(ANALYTICS_DB) as conn:
            try:
                cur = conn.execute(
                    "SELECT target, backup, timestamp FROM rollback_logs ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                )
                records = [
                    {"target": row[0], "backup": row[1], "timestamp": row[2]}
                    for row in cur.fetchall()
                ]
            except sqlite3.Error as exc:
                logging.error("Rollback fetch error: %s", exc)
    return records


def _fetch_correction_history(limit: int = 5) -> List[Dict[str, Any]]:
    history: List[Dict[str, Any]] = []
    if ANALYTICS_DB.exists():
        with sqlite3.connect(ANALYTICS_DB) as conn:
            try:
                cur = conn.execute(
                    "SELECT file_path, compliance_score, ts FROM correction_logs ORDER BY ts DESC LIMIT ?",
                    (limit,),
                )
                history = [
                    {
                        "file_path": row[0],
                        "compliance_score": row[1],
                        "timestamp": row[2],
                    }
                    for row in cur.fetchall()
                ]
            except sqlite3.Error as exc:
                logging.error("History fetch error: %s", exc)
    return history


def _fetch_alerts(limit: int = 5) -> Dict[str, Any]:
    alerts = {"violations": [], "rollbacks": []}
    if ANALYTICS_DB.exists():
        with sqlite3.connect(ANALYTICS_DB) as conn:
            try:
                cur = conn.execute(
                    "SELECT details, timestamp FROM violation_logs ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                )
                alerts["violations"] = [{"details": row[0], "timestamp": row[1]} for row in cur.fetchall()]
                cur = conn.execute(
                    "SELECT target, backup, timestamp FROM rollback_logs ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                )
                alerts["rollbacks"] = [
                    {"target": row[0], "backup": row[1], "timestamp": row[2]} for row in cur.fetchall()
                ]
            except sqlite3.Error as exc:
                logging.error("Alert fetch error: %s", exc)
    return alerts


@app.get("/compliance")
def compliance() -> Any:
    with tqdm(total=1, desc="compliance", unit="step") as pbar:
        data = {
            "metrics": _fetch_metrics(),
            "rollbacks": _fetch_rollbacks(),
        }
        pbar.update(1)
    logging.info("Compliance data served")
    return jsonify(data)


@app.get("/dashboard/compliance")
def dashboard_compliance() -> Any:
    """Alias route for compliance metrics."""
    return compliance()


@app.get("/")
def index() -> Any:
    """Return a minimal dashboard placeholder."""
    return "<h1>Compliance Dashboard</h1>\n<div id='metrics_stream'></div>"
@app.get("/metrics")
def metrics() -> Any:
    start = time.time()
    with tqdm(total=1, desc="metrics", unit="step") as pbar:
        data = _fetch_metrics()
        pbar.update(1)
    etc = f"ETC: {calculate_etc(start, 1, 1)}"
    logging.info("Metrics served | %s", etc)
    return jsonify(data)


@app.get("/metrics_stream")
def metrics_stream() -> Response:
    """Stream metrics as server-sent events for live updates."""
    once = request.args.get("once") == "1"
    if once:
        data = json.dumps(_fetch_metrics())
        return Response(f"data: {data}\n\n", mimetype="text/event-stream")
    interval = int(request.args.get("interval", 5))

    def generate() -> Iterable[str]:
        while True:
            yield f"data: {json.dumps(_fetch_metrics())}\n\n"
            time.sleep(interval)

    return Response(generate(), mimetype="text/event-stream")


@app.get("/alerts_stream")
def alerts_stream() -> Response:
    """Stream alerts as server-sent events for live updates."""

    once = request.args.get("once") == "1"
    if once:
        alerts = json.dumps(_fetch_alerts())
        return Response(f"data: {alerts}\n\n", mimetype="text/event-stream")
    interval = int(request.args.get("interval", 5))

    def generate() -> Iterable[str]:
        while True:
            alerts = _fetch_alerts()
            yield f"data: {json.dumps(alerts)}\n\n"
            time.sleep(interval)

    return Response(generate(), mimetype="text/event-stream")


@app.get("/rollback_alerts")
def rollback_alerts() -> Any:
    data = _fetch_rollbacks()
    return jsonify(data)


@app.get("/rollback_history")
def rollback_history() -> Any:
    """Return full rollback history."""
    return jsonify(_fetch_rollbacks())


@app.get("/alerts")
def alerts() -> Any:
    """Return recent violation and rollback alerts."""
    return jsonify(_fetch_alerts())


@app.get("/violations")
def violations() -> Any:
    """Return recent violation summaries."""
    return jsonify(_fetch_alerts().get("violations", []))


@app.get("/dashboard_info")
def dashboard_info() -> Any:
    start = time.time()
    with tqdm(total=1, desc="dashboard_info", unit="step") as pbar:
        data = {
            "metrics": _fetch_metrics(),
            "rollbacks": _fetch_rollbacks(),
        }
        pbar.update(1)
    etc = f"ETC: {calculate_etc(start, 1, 1)}"
    logging.info("Dashboard info served | %s", etc)
    return jsonify(data)


@app.get("/summary")
def summary() -> Any:
    """Return metrics and alerts in a single payload."""
    start = time.time()
    with tqdm(total=1, desc="summary", unit="step") as pbar:
        data = {
            "metrics": _fetch_metrics(),
            "alerts": _fetch_alerts(),
        }
        pbar.update(1)
    etc = f"ETC: {calculate_etc(start, 1, 1)}"
    logging.info("Summary data served | %s", etc)
    return jsonify(data)


@app.get("/metrics_table")
def metrics_table() -> Any:
    metrics = _fetch_metrics()
    return render_template("metrics_table.html", metrics=metrics)


@app.get("/compliance_metrics")
def compliance_metrics_page() -> Any:
    metrics = _fetch_metrics()
    return render_template("html/compliance_metrics.html", metrics=metrics)


@app.get("/health")
def health() -> Any:
    start = time.time()
    with tqdm(total=1, desc="health", unit="step") as pbar:
        pbar.update(1)
    etc = f"ETC: {calculate_etc(start, 1, 1)}"
    logging.info("Health check served | %s", etc)
    return jsonify({"status": "ok"})


@app.get("/error")
def error() -> Any:
    """Simulate an error for monitoring checks."""
    return jsonify({"status": "error", "message": "simulated failure"}), 500


@app.get("/reports")
def reports() -> Any:
    start = time.time()
    with tqdm(total=1, desc="reports", unit="step") as pbar:
        data = _fetch_rollbacks()
        pbar.update(1)
    etc = f"ETC: {calculate_etc(start, 1, 1)}"
    logging.info("Reports served | %s", etc)
    return jsonify(data)


@app.get("/rollback_logs")
def rollback_logs() -> Any:
    """Expose recent rollback events as JSON."""
    return jsonify(_fetch_rollbacks())


@app.post("/rollback")
def rollback() -> Any:
    """Trigger a rollback for the provided target."""
    data = request.get_json(silent=True) or {}
    target = data.get("target")
    backup = data.get("backup")
    if not target:
        return jsonify({"error": "target required"}), 400
    CorrectionLoggerRollback(ANALYTICS_DB).auto_rollback(
        Path(target), Path(backup) if backup else None
    )
    return jsonify({"status": "ok"})


@app.get("/realtime_metrics")
def realtime_metrics() -> Any:
    data = {
        "metrics": _fetch_metrics(),
        "corrections": _fetch_correction_history(),
    }
    return jsonify(data)


@app.get("/correction_history")
def correction_history() -> Any:
    return jsonify(_fetch_correction_history())


@app.get("/corrections")
def corrections() -> Any:
    """Render correction history using an HTML template."""
    history = _fetch_correction_history()
    return render_template("corrections.html", corrections=history)


@app.get("/dashboard/corrections")
def dashboard_corrections() -> Any:
    """Alias route for the corrections page."""
    return corrections()


def calculate_etc(start_time: float, current_progress: int, total_work: int) -> str:
    elapsed = time.time() - start_time
    if current_progress > 0:
        total_estimated = elapsed / (current_progress / total_work)
        remaining = total_estimated - elapsed
        return f"{remaining:.2f}s remaining"
    return "N/A"


if __name__ == "__main__":
    app.run(port=5000)
