"""Minimal Flask dashboard displaying compliance metrics and rollback controls."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List

from flask import Flask, jsonify, render_template, request, Response

from scripts.correction_logger_and_rollback import CorrectionLoggerRollback

APP_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = APP_DIR / "templates"
METRICS_PATH = Path("dashboard/metrics.json")
CORRECTIONS_DIR = Path("dashboard/compliance")
ANALYTICS_DB = Path("databases/analytics.db")

app = Flask(__name__, template_folder=str(TEMPLATES_DIR))


def _load_json(path: Path) -> Any:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def get_metrics() -> Any:
    return _load_json(METRICS_PATH)


def get_corrections() -> List[dict]:
    summary = _load_json(CORRECTIONS_DIR / "correction_summary.json")
    return summary.get("corrections", [])


@app.route("/")
def dashboard() -> str:
    metrics = get_metrics().get("metrics", {})
    corrections = get_corrections()
    return render_template("dashboard.html", metrics=metrics, corrections=corrections)


@app.route("/metrics")
def metrics() -> Response:
    return jsonify(get_metrics())


@app.route("/corrections")
def corrections() -> Response:
    return jsonify(get_corrections())


@app.route("/rollback", methods=["POST"])
def trigger_rollback():
    data = request.get_json(silent=True) or request.form
    target = data.get("target")
    backup = data.get("backup")
    if not target:
        return jsonify({"status": "error", "message": "target required"}), 400
    log = CorrectionLoggerRollback(ANALYTICS_DB)
    success = log.auto_rollback(Path(target), Path(backup) if backup else None)
    return jsonify({"status": "ok" if success else "failed"})


if __name__ == "__main__":
    app.run(debug=False, port=5000)
