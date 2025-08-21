"""Expose rollback history and actions for the dashboard."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from flask import Blueprint, jsonify, render_template, request

from scripts.correction_logger_and_rollback import CorrectionLoggerRollback
from src.dashboard.api.logs import (
    ANALYTICS_DB,
    fetch_correction_rollback_events,
)
from src.dashboard.auth import require_session

bp = Blueprint(
    "dashboard_rollbacks",
    __name__,
    template_folder=str(Path(__file__).resolve().parents[1] / "templates"),
)


@bp.route("/rollbacks")
@require_session()
def rollbacks_view() -> str:
    """Render rollback history with manual rollback option."""
    logs = fetch_correction_rollback_events(db_path=ANALYTICS_DB, limit=50)
    return render_template("rollback_logs.html", logs=logs)


@bp.route("/rollback_logs")
@require_session()
def rollback_logs() -> Any:
    """Return recent correction and rollback events as JSON."""
    return jsonify(fetch_correction_rollback_events(db_path=ANALYTICS_DB))


@bp.route("/rollback", methods=["POST"])
@require_session()
def perform_rollback() -> Any:
    """Trigger a rollback for the provided target."""
    data = request.get_json(silent=True) or {}
    target = data.get("target")
    backup = data.get("backup")
    if not target:
        return jsonify({"error": "target required"}), 400
    clr = CorrectionLoggerRollback(ANALYTICS_DB)
    clr.auto_rollback(Path(target), Path(backup) if backup else None)
    return jsonify({"status": "ok"})


__all__ = ["bp"]
