"""Quantum dashboard analytics integration."""

from pathlib import Path
import sqlite3
from typing import Dict

from analytics.predictive_models import predict_next
from web_gui.monitoring.quantum_metrics import quantum_metric

ANALYTICS_DB = Path("databases/analytics.db")


def get_metrics(db_path: Path = ANALYTICS_DB) -> Dict[str, float]:
    """Return quantum analytics with monitoring data."""
    metrics: Dict[str, float] = {
        "avg_importance": 0.0,
        "predicted_importance": 0.0,
        "quantum_score": 0.0,
    }
    if db_path.exists():
        try:
            with sqlite3.connect(db_path) as conn:
                cur = conn.execute(
                    "SELECT AVG(importance_score) FROM quantum_template_tracking",
                )
                (avg,) = cur.fetchone()
                metrics["avg_importance"] = float(avg or 0.0)
                metrics["predicted_importance"] = predict_next([metrics["avg_importance"]])
        except sqlite3.Error:
            pass
    metrics["quantum_score"] = quantum_metric([metrics["avg_importance"]])
    return metrics


__all__ = ["get_metrics"]

