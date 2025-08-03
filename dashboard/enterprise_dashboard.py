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
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template

from utils.validation_utils import validate_enterprise_environment


# Paths to metrics and rollback data
METRICS_FILE = Path(__file__).with_name("metrics.json")
ANALYTICS_DB = Path("databases/analytics.db")


app = Flask(
    __name__,
    template_folder=str(Path(__file__).parent / "templates"),
    static_folder=str(Path(__file__).parent / "static"),
)


def _load_metrics() -> dict[str, Any]:
    """Load dashboard metrics from ``metrics.json``."""
    if METRICS_FILE.exists():
        try:
            return json.loads(METRICS_FILE.read_text())
        except json.JSONDecodeError as exc:  # pragma: no cover - log and fall back
            logging.error("Metrics decode error: %s", exc)
    return {"metrics": {}, "notes": []}


def _load_rollbacks(limit: int = 10) -> list[dict[str, Any]]:
    """Return recent rollback log entries from ``analytics.db``."""
    records: list[dict[str, Any]] = []
    if ANALYTICS_DB.exists():
        with sqlite3.connect(ANALYTICS_DB) as conn:
            try:
                cur = conn.execute(
                    "SELECT timestamp, target, backup FROM rollback_logs ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                )
                records = [
                    {"timestamp": row[0], "target": row[1], "backup": row[2]}
                    for row in cur.fetchall()
                ]
            except sqlite3.Error as exc:  # pragma: no cover - log and continue
                logging.error("Rollback fetch error: %s", exc)
    return records


@app.route("/")
def index() -> str:
    """Render the main dashboard page."""
    return render_template("dashboard.html")


@app.route("/metrics")
def metrics() -> Any:
    """Return compliance metrics as JSON."""
    return jsonify(_load_metrics())


@app.route("/rollback-logs")
def rollback_logs() -> Any:
    """Return recent rollback log entries as JSON."""
    return jsonify(_load_rollbacks())


@app.route("/metrics/view")
def metrics_view() -> str:
    """Render a simple HTML view of the metrics."""
    return render_template("metrics.html", data=_load_metrics())


@app.route("/rollback-logs/view")
def rollback_logs_view() -> str:
    """Render a simple HTML view of rollback logs."""
    return render_template("rollback_logs.html", logs=_load_rollbacks())


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
    logging.info("Recent rollbacks: %s", _load_rollbacks())
    port = int(os.getenv("FLASK_RUN_PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=bool(__name__ == "__main__"))


if __name__ == "__main__":  # pragma: no cover - manual execution
    main()

