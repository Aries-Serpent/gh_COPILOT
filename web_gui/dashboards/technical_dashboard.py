"""Technical dashboard analytics integration."""

from pathlib import Path
import sqlite3
from typing import Dict

from analytics.performance_analysis import summarize_performance
from web_gui.monitoring.performance_metrics import collect_performance_metrics

ANALYTICS_DB = Path("databases/analytics.db")


def get_metrics(db_path: Path = ANALYTICS_DB) -> Dict[str, float]:
    """Return technical analytics with system performance data."""
    metrics: Dict[str, float] = {"scripts": 0.0, "avg_scripts": 0.0}
    if db_path.exists():
        try:
            with sqlite3.connect(db_path) as conn:
                cur = conn.execute(
                    "SELECT COUNT(*) FROM enhanced_script_tracking",
                )
                (count,) = cur.fetchone()
                metrics["scripts"] = float(count or 0)
                metrics["avg_scripts"] = summarize_performance({"scripts": metrics["scripts"]})
        except sqlite3.Error:
            pass
    metrics.update(collect_performance_metrics())
    return metrics


__all__ = ["get_metrics"]

