"""Expose correction log entries for the dashboard."""

from __future__ import annotations

from typing import Any
from flask import Blueprint, jsonify

from src.dashboard.api.logs import (
    ANALYTICS_DB,
    fetch_recent_correction_logs,
)
from src.dashboard.auth import require_session

bp = Blueprint("dashboard_corrections", __name__)

@bp.route("/corrections/logs")
@require_session()
def correction_logs() -> Any:
    """Return recent correction log entries as JSON."""
    return jsonify(fetch_recent_correction_logs(db_path=ANALYTICS_DB))

__all__ = ["bp", "ANALYTICS_DB"]
