"""Quantum dashboard analytics integration."""

from pathlib import Path
import sqlite3
from typing import Dict

ANALYTICS_DB = Path("databases/analytics.db")


def get_metrics(db_path: Path = ANALYTICS_DB) -> Dict[str, float]:
    """Return quantum related analytics."""
    metrics = {"avg_importance": 0.0}
    if db_path.exists():
        try:
            with sqlite3.connect(db_path) as conn:
                cur = conn.execute(
                    "SELECT AVG(importance_score) FROM quantum_template_tracking",
                )
                (avg,) = cur.fetchone()
                metrics["avg_importance"] = float(avg or 0.0)
        except sqlite3.Error:
            pass
    return metrics


__all__ = ["get_metrics"]

