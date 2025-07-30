#!/usr/bin/env python3
"""Enterprise compliance dashboard with real-time metrics."""

from __future__ import annotations

import json
import logging
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

from flask import Flask, Response, jsonify, request
from tqdm import tqdm

from config.secret_manager import get_secret

ANALYTICS_DB = Path("databases/analytics.db")
COMPLIANCE_DIR = Path("dashboard/compliance")

app = Flask(__name__)
app.secret_key = get_secret("FLASK_SECRET_KEY", "dev_key")
LOG_FILE = Path("logs/dashboard") / "dashboard.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(level=logging.INFO, handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])


def _fetch_metrics() -> Dict[str, Any]:
    metrics = {"placeholder_removal": 0, "open_placeholders": 0, "compliance_score": 0.0}
    if ANALYTICS_DB.exists():
        with sqlite3.connect(ANALYTICS_DB) as conn:
            cur = conn.cursor()
            try:
                cur.execute("SELECT COUNT(*) FROM todo_fixme_tracking WHERE resolved=1")
                metrics["placeholder_removal"] = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM todo_fixme_tracking WHERE resolved=0")
                metrics["open_placeholders"] = cur.fetchone()[0]
                cur.execute("SELECT AVG(compliance_score) FROM corrections")
                val = cur.fetchone()[0]
                metrics["compliance_score"] = float(val) if val is not None else 0.0
            except sqlite3.Error as exc:
                logging.error("Metric fetch error: %s", exc)
    return metrics


def _fetch_rollbacks() -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    file = COMPLIANCE_DIR / "correction_summary.json"
    if file.exists():
        try:
            data = json.loads(file.read_text())
            records = data.get("corrections", [])
        except json.JSONDecodeError:
            logging.warning("Invalid correction summary JSON")
    return records


def _fetch_correction_history(limit: int = 5) -> List[Dict[str, Any]]:
    history: List[Dict[str, Any]] = []
    if ANALYTICS_DB.exists():
        with sqlite3.connect(ANALYTICS_DB) as conn:
            try:
                cur = conn.execute(
                    "SELECT file_path, compliance_score, ts FROM correction_logs "
                    "ORDER BY ts DESC LIMIT ?",
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
def index() -> str:
    return "Compliance Dashboard"


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

    def generate() -> Iterable[str]:
        metrics = _fetch_metrics()
        yield f"data: {json.dumps(metrics)}\n\n"
        if once:
            return
        while True:
            time.sleep(5)
            metrics = _fetch_metrics()
            yield f"data: {json.dumps(metrics)}\n\n"

    return Response(generate(), mimetype="text/event-stream")


@app.get("/rollback_alerts")
def rollback_alerts() -> Any:
    data = _fetch_rollbacks()
    return jsonify(data)


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


@app.get("/health")
def health() -> Any:
    start = time.time()
    with tqdm(total=1, desc="health", unit="step") as pbar:
        pbar.update(1)
    etc = f"ETC: {calculate_etc(start, 1, 1)}"
    logging.info("Health check served | %s", etc)
    return jsonify({"status": "ok"})


@app.get("/reports")
def reports() -> Any:
    start = time.time()
    with tqdm(total=1, desc="reports", unit="step") as pbar:
        data = _fetch_rollbacks()
        pbar.update(1)
    etc = f"ETC: {calculate_etc(start, 1, 1)}"
    logging.info("Reports served | %s", etc)
    return jsonify(data)


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


def calculate_etc(start_time: float, current_progress: int, total_work: int) -> str:
    elapsed = time.time() - start_time
    if current_progress > 0:
        total_estimated = elapsed / (current_progress / total_work)
        remaining = total_estimated - elapsed
        return f"{remaining:.2f}s remaining"
    return "N/A"


if __name__ == "__main__":
    app.run(port=5000)
