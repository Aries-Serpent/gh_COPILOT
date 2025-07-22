from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from datetime import datetime
from tqdm import tqdm
from flask import Flask, jsonify, request

from scripts.correction_logger_and_rollback import CorrectionLoggerRollback

METRICS_PATH = Path("dashboard/metrics.json")
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


__all__ = ["app"]
