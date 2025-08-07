"""Flask entry point for the enterprise dashboard.

This minimal application exposes JSON routes for compliance metrics
and rollback logs along with a simple HTML dashboard.  The module is
intentionally lightweight so it can run independently of the
``web_gui`` package while still validating the expected enterprise
environment variables.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from flask import Flask, Response, jsonify, render_template, request
from tqdm import tqdm

from scripts.correction_logger_and_rollback import CorrectionLoggerRollback
from database_first_synchronization_engine import list_events
from enterprise_modules.compliance import calculate_composite_score
from utils.validation_utils import validate_enterprise_environment


# Paths to metrics and rollback data
COMPLIANCE_DIR = Path(__file__).parent / "compliance"
METRICS_FILE = COMPLIANCE_DIR / "metrics.json"
CORRECTIONS_FILE = COMPLIANCE_DIR / "correction_summary.json"
ANALYTICS_DB = Path("databases/analytics.db")


app = Flask(
    __name__,
    template_folder=str(Path(__file__).parent / "templates"),
    static_folder=str(Path(__file__).parent / "static"),
)


def _load_metrics() -> dict[str, Any]:
    """Load dashboard metrics from ``metrics.json`` and analytics.db."""
    metrics: dict[str, Any] = {}
    if METRICS_FILE.exists():
        try:
            metrics = json.loads(METRICS_FILE.read_text()).get("metrics", {})
        except json.JSONDecodeError as exc:  # pragma: no cover - log and fall back
            logging.error("Metrics decode error: %s", exc)
    if ANALYTICS_DB.exists():
        with sqlite3.connect(ANALYTICS_DB) as conn:
            conn.row_factory = sqlite3.Row
            try:
                cur = conn.execute(
                    """
                    SELECT ruff_issues, tests_passed, tests_failed,
                           placeholders_open, placeholders_resolved, ts
                    FROM code_quality_metrics
                    ORDER BY id DESC LIMIT 1
                    """
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
                    metrics["compliance_score"] = score
                    metrics["composite_score"] = score
                    metrics["score_breakdown"] = breakdown
                    metrics["last_audit_date"] = row["ts"]
            except sqlite3.Error as exc:  # pragma: no cover - log and continue
                logging.error("Composite fetch error: %s", exc)
            try:
                cur = conn.execute("SELECT COUNT(*) FROM placeholder_audit")
                metrics["violation_count"] = cur.fetchone()[0]
                cur = conn.execute("SELECT COUNT(*) FROM rollback_logs")
                metrics["rollback_count"] = cur.fetchone()[0]
            except sqlite3.Error as exc:  # pragma: no cover - log and continue
                logging.error("Count fetch error: %s", exc)
    metrics.setdefault("violation_count", 0)
    metrics.setdefault("rollback_count", 0)
    metrics.setdefault("timestamp", datetime.utcnow().isoformat())
    return {"metrics": metrics, "notes": []}


def _load_corrections() -> dict[str, Any]:
    """Return correction summary data."""
    if CORRECTIONS_FILE.exists():
        try:
            return json.loads(CORRECTIONS_FILE.read_text())
        except json.JSONDecodeError as exc:  # pragma: no cover - log and continue
            logging.error("Corrections decode error: %s", exc)
    return {}


def get_rollback_logs(limit: int = 10) -> list[dict[str, Any]]:
    """Return recent rollback log entries from ``analytics.db``."""
    records: list[dict[str, Any]] = []
    if not ANALYTICS_DB.exists():
        return records
    try:
        with sqlite3.connect(ANALYTICS_DB) as conn:
            cur = conn.execute(
                "SELECT timestamp, target, backup FROM rollback_logs ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            )
            records = [{"timestamp": row[0], "target": row[1], "backup": row[2]} for row in cur.fetchall()]
    except sqlite3.Error as exc:  # pragma: no cover - log and continue
        logging.error("Rollback fetch error: %s", exc)
    return records


def _get_violation_logs(limit: int = 50) -> list[dict[str, Any]]:
    """Return recent violation log entries from ``analytics.db``."""
    rows: list[dict[str, Any]] = []
    if not ANALYTICS_DB.exists():
        return rows
    try:
        with sqlite3.connect(ANALYTICS_DB) as conn:
            cur = conn.execute(
                "SELECT timestamp, details FROM violation_logs ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            )
            rows = [dict(timestamp=r[0], details=r[1]) for r in cur.fetchall()]
    except sqlite3.Error as exc:  # pragma: no cover - log and continue
        logging.error("Violation fetch error: %s", exc)
    return rows


def _get_placeholder_audit(limit: int = 100) -> list[dict[str, Any]]:
    """Return placeholder audit entries from ``analytics.db``."""
    rows: list[dict[str, Any]] = []
    if not ANALYTICS_DB.exists():
        return rows
    try:
        with sqlite3.connect(ANALYTICS_DB) as conn:
            cur = conn.execute(
                "SELECT file_path, line_number, placeholder_type, context FROM placeholder_audit ORDER BY id DESC LIMIT ?",
                (limit,),
            )
            rows = [
                {
                    "file_path": r[0],
                    "line_number": r[1],
                    "placeholder_type": r[2],
                    "context": r[3],
                }
                for r in cur.fetchall()
            ]
    except sqlite3.Error as exc:  # pragma: no cover - log and continue
        logging.error("Placeholder audit fetch error: %s", exc)
    return rows


def _load_sync_events(limit: int = 10) -> list[dict[str, Any]]:
    """Return recent synchronization events from ``analytics.db``."""
    try:
        return list_events(ANALYTICS_DB, limit)
    except sqlite3.Error as exc:  # pragma: no cover - log and continue
        logging.error("Sync events fetch error: %s", exc)
    return []


def _load_audit_results(limit: int = 50) -> list[dict[str, Any]]:
    """Return aggregated placeholder audit results from ``analytics.db``."""
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
    except sqlite3.Error as exc:  # pragma: no cover - log and continue
        logging.error("Audit fetch error: %s", exc)
    return rows


@app.route("/")
def index() -> str:
    """Render the main dashboard page."""
    return render_template(
        "dashboard.html",
        metrics=_load_metrics().get("metrics", {}),
        rollbacks=get_rollback_logs(),
    )


@app.route("/metrics")
def metrics() -> Any:
    """Return compliance metrics as JSON."""
    return jsonify(_load_metrics())


@app.route("/metrics_stream")
def metrics_stream() -> Response:
    """Stream metrics as server-sent events.

    Supports optional ``once`` query parameter to send a single event and
    ``interval`` to control update frequency in seconds.
    """

    once = request.args.get("once") == "1"
    interval = int(request.args.get("interval", "5"))

    def generate() -> Any:
        while True:
            payload = json.dumps(_load_metrics().get("metrics", {}))
            yield f"data: {payload}\n\n"
            if once:
                break
            time.sleep(interval)

    return Response(generate(), mimetype="text/event-stream")


@app.route("/rollback-logs")
def rollback_logs() -> Any:
    """Return recent rollback log entries as JSON."""
    return jsonify(get_rollback_logs())


@app.route("/audit-results")
def audit_results() -> Any:
    """Return placeholder audit results as JSON."""
    return jsonify(_load_audit_results())


@app.route("/sync-events")
def sync_events() -> Any:
    """Return recent synchronization events as JSON."""
    return jsonify(_load_sync_events())


@app.route("/corrections")
def corrections() -> Any:
    """Return correction summary data as JSON."""
    return jsonify(_load_corrections())


@app.route("/compliance")
def compliance() -> Any:
    """Return combined metrics and correction summary as JSON."""
    metrics = _load_metrics().get("metrics", {})
    corrections = _load_corrections().get("corrections", [])
    return jsonify({"metrics": metrics, "corrections": corrections})


@app.route("/violations")
def violations() -> Any:
    """Return recent violation log entries as JSON."""
    return jsonify({"violations": _get_violation_logs()})


@app.route("/placeholder-audit")
def placeholder_audit() -> Any:
    """Return placeholder audit entries as JSON."""
    return jsonify({"results": _get_placeholder_audit()})


@app.post("/rollback")
def trigger_rollback() -> Any:
    """Trigger an automatic rollback via ``CorrectionLoggerRollback``."""
    payload = request.get_json(force=True) or {}
    target = Path(payload.get("target", ""))
    backup = payload.get("backup")
    rollbacker = CorrectionLoggerRollback(ANALYTICS_DB)
    with tqdm(total=1, desc="rollback", unit="step") as bar:
        ok = rollbacker.auto_rollback(target, Path(backup) if backup else None)
        bar.update(1)
    return jsonify({"status": "ok" if ok else "failed"})


@app.route("/dashboard/compliance")
def dashboard_compliance() -> Any:
    """Return combined metrics and rollback logs."""
    data = {
        "metrics": _load_metrics().get("metrics", {}),
        "rollbacks": get_rollback_logs(),
    }
    return jsonify(data)


@app.route("/metrics/view")
def metrics_view() -> str:
    """Render a simple HTML view of the metrics."""
    metrics_data = _load_metrics().get("metrics", {})
    return render_template("metrics.html", metrics=metrics_data)


@app.route("/rollback-logs/view")
def rollback_logs_view() -> str:
    """Render a simple HTML view of rollback logs."""
    return render_template("rollback_logs.html", logs=get_rollback_logs())


@app.route("/audit-results/view")
def audit_results_view() -> str:
    """Render an HTML view of audit results."""
    return render_template("audit_results.html", results=_load_audit_results())


@app.route("/sync-events/view")
def sync_events_view() -> str:
    """Render an HTML view of synchronization events."""
    return render_template("sync_events.html", events=_load_sync_events())


@app.route("/dashboard/compliance/view")
def dashboard_compliance_view() -> str:
    """Render an HTML view of compliance metrics."""
    metrics_data = _load_metrics().get("metrics", {})
    return render_template("metrics.html", metrics=metrics_data)


def _validate_environment() -> None:
    """Validate required environment variables and log their values."""
    try:
        validate_enterprise_environment()
    except EnvironmentError as exc:  # pragma: no cover - fails fast
        logging.error("Environment validation failed: %s", exc)
        raise
    for var in ["GH_COPILOT_WORKSPACE", "GH_COPILOT_BACKUP_ROOT"]:
        logging.info("%s=%s", var, os.getenv(var))


def main() -> None:
    """Start the Flask development server."""
    logging.basicConfig(level=logging.INFO)
    _validate_environment()
    logging.info("Startup metrics: %s", _load_metrics().get("metrics"))
    logging.info("Recent rollbacks: %s", get_rollback_logs())
    port = int(os.getenv("FLASK_RUN_PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=bool(__name__ == "__main__"))


if __name__ == "__main__":  # pragma: no cover - manual execution
    main()
