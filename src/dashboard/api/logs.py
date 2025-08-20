from __future__ import annotations

"""API utilities for exposing correction and rollback logs."""

from pathlib import Path
import sqlite3
from typing import Any, Dict, List

from flask import Blueprint, jsonify

from src.dashboard.auth import require_session

# Default path to analytics database storing correction logs
ANALYTICS_DB = Path("databases/analytics.db")

# Blueprint allowing the module to be registered with a Flask app
bp = Blueprint("correction_logs", __name__)


def fetch_recent_correction_logs(limit: int = 10, db_path: Path = ANALYTICS_DB) -> List[Dict[str, Any]]:
    """Return the most recent correction log entries.

    Parameters
    ----------
    limit:
        Maximum number of log entries to return.
    db_path:
        Path to the SQLite database containing a ``correction_logs`` table.
    """

    rows: List[Dict[str, Any]] = []
    if db_path.exists():
        with sqlite3.connect(db_path) as conn:
            cur = conn.execute(
                "SELECT timestamp, path, status FROM correction_logs ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            )
            rows = [
                {"timestamp": r[0], "path": r[1], "status": r[2]} for r in cur.fetchall()
            ]
    return rows


def fetch_correction_rollback_events(
    limit: int = 10, db_path: Path = ANALYTICS_DB
) -> List[Dict[str, Any]]:
    """Return combined correction and rollback events.

    Parameters
    ----------
    limit:
        Maximum number of events to return.
    db_path:
        Path to the SQLite database containing a ``correction_rollback_events`` table.
    """

    rows: List[Dict[str, Any]] = []
    if db_path.exists():
        try:
            with sqlite3.connect(db_path) as conn:
                cur = conn.execute(
                    """
                    SELECT event_type, target, backup, status, timestamp
                    FROM correction_rollback_events
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    (limit,),
                )
                rows = [
                    {
                        "event_type": r[0],
                        "target": r[1],
                        "backup": r[2],
                        "status": r[3],
                        "timestamp": r[4],
                    }
                    for r in cur.fetchall()
                ]
        except sqlite3.Error:
            # Table may not exist yet; return empty list
            rows = []
    return rows


@bp.route("/correction-logs")
@require_session()
def correction_logs() -> Any:
    """Flask route exposing recent correction logs as JSON."""
    return jsonify(fetch_recent_correction_logs(db_path=ANALYTICS_DB))


@bp.route("/rollback_logs")
@require_session()
def rollback_logs() -> Any:
    """Flask route exposing recent correction and rollback events as JSON."""
    return jsonify(fetch_correction_rollback_events(db_path=ANALYTICS_DB))


__all__ = [
    "bp",
    "ANALYTICS_DB",
    "fetch_recent_correction_logs",
    "fetch_correction_rollback_events",
]
