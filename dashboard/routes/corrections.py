"""Expose correction log entries for the dashboard."""

from __future__ import annotations

from typing import Any
from flask import Blueprint, jsonify, request

from src.dashboard.api.logs import (
    ANALYTICS_DB,
    fetch_recent_correction_logs,
)
from src.dashboard.auth import require_session

bp = Blueprint("dashboard_corrections", __name__)

@bp.route("/corrections/logs")
@require_session()
def correction_logs() -> Any:
    """Return recent correction log entries as JSON.

    Supports an optional ``limit`` query parameter to control the number of
    rows returned, enabling simple pagination on the client side.
    """
    limit = request.args.get("limit", type=int)
    kwargs = {"db_path": ANALYTICS_DB}
    if limit:
        kwargs["limit"] = limit
    return jsonify(fetch_recent_correction_logs(**kwargs))

__all__ = ["bp", "ANALYTICS_DB"]
