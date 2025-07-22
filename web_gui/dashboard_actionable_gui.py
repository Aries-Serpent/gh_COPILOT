from __future__ import annotations

import json
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
    data = {}
    if METRICS_PATH.exists():
        data = json.loads(METRICS_PATH.read_text())
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
    """Return recent compliance metrics from analytics.db."""
    metrics = []
    if ANALYTICS_DB.exists():
        with sqlite3.connect(ANALYTICS_DB) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS compliance_metrics (ts TEXT, metric TEXT, value REAL)"
            )
            rows = conn.execute(
                "SELECT ts, metric, value FROM compliance_metrics ORDER BY ts DESC LIMIT 10"
            ).fetchall()
            metrics = [dict(ts=row[0], metric=row[1], value=row[2]) for row in rows]
    return jsonify({"metrics": metrics, "timestamp": datetime.utcnow().isoformat()})


@app.post("/rollback")
def trigger_rollback():
    payload = request.get_json(force=True) or {}
    target = Path(payload.get("target", ""))
    backup = payload.get("backup")
    rollbacker = CorrectionLoggerRollback(ANALYTICS_DB)
    ok = rollbacker.auto_rollback(target, Path(backup) if backup else None)
    return jsonify({"status": "ok" if ok else "failed"})


__all__ = ["app"]
