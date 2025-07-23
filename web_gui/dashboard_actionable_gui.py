from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime

from scripts.correction_logger_and_rollback import CorrectionLoggerRollback

METRICS_PATH = Path("dashboard/metrics.json")
CORRECTIONS_DIR = Path("dashboard/compliance")
ANALYTICS_DB = Path("databases/analytics.db")

app = Flask(__name__)


@app.get("/metrics")
def get_metrics():
    metrics = {
        "compliance_score": 0.0,
        "violation_count": 0,
        "rollback_count": 0,
    }
    if ANALYTICS_DB.exists():
        with sqlite3.connect(ANALYTICS_DB) as conn:
            cur = conn.cursor()
            cur.execute("SELECT AVG(compliance_score) FROM correction_logs")
            row = cur.fetchone()
            metrics["compliance_score"] = float(row[0]) if row and row[0] is not None else 0.0
            cur.execute("SELECT COUNT(*) FROM violation_logs")
            metrics["violation_count"] = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM rollback_logs")
            metrics["rollback_count"] = cur.fetchone()[0]
    return jsonify(metrics)


@app.get("/corrections")
def get_corrections():
    summary = CORRECTIONS_DIR / "correction_summary.json"
    data = {}
    if summary.exists():
        data = json.loads(summary.read_text())
    return jsonify(data)


@app.get("/violations")
def get_violations():
    logs = []
    if ANALYTICS_DB.exists():
        with sqlite3.connect(ANALYTICS_DB) as conn:
            cur = conn.cursor()
            cur.execute("SELECT timestamp, details FROM violation_logs ORDER BY timestamp DESC LIMIT 50")
            logs = [dict(timestamp=row[0], details=row[1]) for row in cur.fetchall()]
    return jsonify({"violations": logs})


@app.post("/rollback")
def trigger_rollback():
    payload = request.get_json(force=True) or {}
    target = Path(payload.get("target", ""))
    backup = payload.get("backup")
    rollbacker = CorrectionLoggerRollback(ANALYTICS_DB)
    ok = rollbacker.auto_rollback(target, Path(backup) if backup else None)
    return jsonify({"status": "ok" if ok else "failed"})


__all__ = ["app"]
