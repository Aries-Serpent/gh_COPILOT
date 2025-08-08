"""API endpoint exposing recent corrections from synchronization events."""

from __future__ import annotations

from pathlib import Path
import sqlite3
from typing import Any, Dict, List

from flask import Blueprint, jsonify

from src.dashboard.auth import require_session


ANALYTICS_DB = Path("databases/analytics.db")

bp = Blueprint("corrections", __name__)


def fetch_recent_corrections(limit: int = 10, db_path: Path = ANALYTICS_DB) -> List[Dict[str, Any]]:
    """Return the most recent synchronization corrections."""

    rows: List[Dict[str, Any]] = []
    if db_path.exists():
        with sqlite3.connect(db_path) as conn:
            cur = conn.execute(
                "SELECT ts, source, target FROM sync_events_log ORDER BY ts DESC LIMIT ?",
                (limit,),
            )
            rows = [
                {"timestamp": r[0], "entity": r[1], "resolution": r[2]}
                for r in cur.fetchall()
            ]
    return rows


@bp.route("/api/corrections")
@require_session()
def corrections() -> Any:
    """Flask route exposing recent synchronization corrections as JSON."""
    return jsonify(fetch_recent_corrections(db_path=ANALYTICS_DB))


__all__ = ["bp", "fetch_recent_corrections", "ANALYTICS_DB"]

