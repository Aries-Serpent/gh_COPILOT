from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from tqdm import tqdm

from scripts.correction_logger_and_rollback import CorrectionLoggerRollback

METRICS_PATH = Path("dashboard/compliance/metrics.json")
CORRECTIONS_DIR = Path("dashboard/compliance")
ANALYTICS_DB = Path("databases/analytics.db")

app = Flask(__name__)


def fetch_db_metrics() -> dict:
    """Fetch real-time metrics from analytics.db."""
    data = {
        "placeholder_removal": 0,
        "compliance_score": 0.0,
        "violation_count": 0,
        "rollback_count": 0,
        "timestamp": datetime.utcnow().isoformat(),
    }
    if not ANALYTICS_DB.exists():
        return data
    with sqlite3.connect(ANALYTICS_DB) as conn:
        cur = conn.cursor()
        try:
            cur.execute("SELECT COUNT(*) FROM placeholder_audit")
            data["violation_count"] = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM rollback_logs")
            data["rollback_count"] = cur.fetchone()[0]
        except sqlite3.Error:
            pass
    return data


@app.get("/metrics")
def get_metrics():
    data = fetch_db_metrics()
    if METRICS_PATH.exists():
        file_data = json.loads(METRICS_PATH.read_text())
        data.update(file_data)
    return jsonify(data)


@app.get("/corrections")
def get_corrections():
    summary = CORRECTIONS_DIR / "correction_summary.json"
    data = {}
    if summary.exists():
        data = json.loads(summary.read_text())
    return jsonify(data)


@app.get("/compliance")
def get_compliance():
    """Return combined metrics and correction summary."""
    metrics = fetch_db_metrics()
    summary_file = CORRECTIONS_DIR / "correction_summary.json"
    corrections = []
    if summary_file.exists():
        try:
            corrections = json.loads(summary_file.read_text()).get("corrections", [])
        except json.JSONDecodeError:
            corrections = []
    return jsonify({"metrics": metrics, "corrections": corrections})


@app.get("/violations")
def get_violations():
    logs = []
    if ANALYTICS_DB.exists():
        with sqlite3.connect(ANALYTICS_DB) as conn:
            cur = conn.cursor()
            cur.execute("SELECT timestamp, details FROM violation_logs ORDER BY timestamp DESC LIMIT 50")
            logs = [dict(timestamp=row[0], details=row[1]) for row in cur.fetchall()]
    return jsonify({"violations": logs})


@app.get("/placeholder-audit")
def get_placeholder_audit():
    entries = []
    if ANALYTICS_DB.exists():
        with sqlite3.connect(ANALYTICS_DB) as conn:
            try:
                cur = conn.execute(
                    "SELECT file_path, line_number, placeholder_type, context FROM placeholder_audit ORDER BY id DESC LIMIT 100"
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


@app.post("/rollback")
def trigger_rollback():
    payload = request.get_json(force=True) or {}
    target = Path(payload.get("target", ""))
    backup = payload.get("backup")
    rollbacker = CorrectionLoggerRollback(ANALYTICS_DB)
    with tqdm(total=1, desc="rollback", unit="step") as bar:
        ok = rollbacker.auto_rollback(target, Path(backup) if backup else None)
        bar.update(1)
    return jsonify({"status": "ok" if ok else "failed"})


@app.get("/dashboard/compliance")
def compliance_dashboard():
    """Render compliance metrics page."""
    metrics = fetch_db_metrics()
    return render_template("compliance_metrics.html", metrics=metrics)


@app.get("/dashboard/rollback")
def rollback_dashboard():
    """Render rollback logs page."""
    logs = []
    if ANALYTICS_DB.exists():
        with sqlite3.connect(ANALYTICS_DB) as conn:
            cur = conn.cursor()
            try:
                cur.execute(
                    "SELECT timestamp, target, backup FROM rollback_logs ORDER BY timestamp DESC LIMIT 50"
                )
                logs = [
                    {"timestamp": row[0], "target": row[1], "backup": row[2]}
                    for row in cur.fetchall()
                ]
            except sqlite3.Error:
                pass
    return render_template("rollback_logs.html", logs=logs)


__all__ = ["app"]
