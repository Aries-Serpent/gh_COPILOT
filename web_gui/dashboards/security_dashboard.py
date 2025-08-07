"""Security dashboard analytics integration."""

from pathlib import Path
import sqlite3
from typing import Dict

from analytics.user_behavior import log_user_action

ANALYTICS_DB = Path("databases/analytics.db")


ACTION_LOG: Dict[str, int] = {}


def get_metrics(db_path: Path = ANALYTICS_DB) -> Dict[str, int]:
    """Return basic security analytics."""
    metrics = {"open_issues": 0, "views": 0}
    if db_path.exists():
        try:
            with sqlite3.connect(db_path) as conn:
                cur = conn.execute(
                    "SELECT COUNT(*) FROM violation_logs WHERE status='open'",
                )
                (count,) = cur.fetchone()
                metrics["open_issues"] = int(count or 0)
        except sqlite3.Error:
            pass
    metrics["views"] = log_user_action("security_dashboard", ACTION_LOG)["security_dashboard"]
    return metrics


__all__ = ["get_metrics"]

