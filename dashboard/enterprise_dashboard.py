"""Start the enterprise Flask dashboard.

This wrapper loads ``app`` from :mod:`web_gui.scripts.flask_apps.enterprise_dashboard`
and exposes a ``main`` entry point for command-line execution. The dashboard
listens on ``FLASK_RUN_PORT`` when set, falling back to port ``5000``.
"""

from __future__ import annotations

import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from web_gui.scripts.flask_apps.enterprise_dashboard import (
    app,
    _fetch_metrics,
    _fetch_alerts,
    metrics_stream,
)

ANALYTICS_DB = Path("databases/analytics.db")
from utils.validation_utils import validate_enterprise_environment


def _fetch_correction_history(limit: int = 5) -> list[dict[str, str | float]]:
    """Return recent correction log entries."""
    history: list[dict[str, str | float]] = []
    if ANALYTICS_DB.exists():
        with sqlite3.connect(ANALYTICS_DB) as conn:
            try:
                cur = conn.execute(
                    "SELECT file_path, compliance_score, ts FROM correction_logs ORDER BY ts DESC LIMIT ?",
                    (limit,),
                )
                history = [
                    {
                        "file_path": row[0],
                        "compliance_score": row[1],
                        "timestamp": row[2],
                    }
                    for row in cur.fetchall()
                ]
            except sqlite3.Error as exc:
                logging.error("History fetch error: %s", exc)
    return history


__all__ = ["app", "main", "metrics_stream"]


def _validate_environment() -> None:
    """Validate required environment variables."""
    try:
        validate_enterprise_environment()
    except EnvironmentError as exc:
        logging.error("Environment validation failed: %s", exc)
        raise
    for var in ["GH_COPILOT_WORKSPACE", "GH_COPILOT_BACKUP_ROOT"]:
        logging.info("%s=%s", var, os.getenv(var))


def main() -> None:
    """Run the wrapped Flask app with startup logging."""
    logging.basicConfig(level=logging.INFO)
    logging.info("Dashboard starting at %s", datetime.utcnow().isoformat())
    _validate_environment()
    logging.info("Startup metrics: %s", _fetch_metrics())
    logging.info("Startup alerts: %s", _fetch_alerts())
    logging.info("Recent corrections: %s", _fetch_correction_history())
    port = int(os.getenv("FLASK_RUN_PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=bool(__name__ == "__main__"))


if __name__ == "__main__":
    main()
