"""Security dashboard analytics integration."""

from pathlib import Path
import sqlite3
from typing import Dict

from analytics.user_behavior import log_user_action
from web_gui.monitoring.compliance_monitoring import check_compliance

ANALYTICS_DB = Path("databases/analytics.db")


ACTION_LOG: Dict[str, int] = {}


def get_metrics(db_path: Path = ANALYTICS_DB) -> Dict[str, int]:
    """Return security analytics with compliance status."""
    metrics = {"open_issues": 0, "views": 0, "compliant": 0}
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
    metrics["compliant"] = 1 if check_compliance({"policy": "default", "status": "ok"}) else 0
    return metrics


__all__ = ["get_metrics"]

