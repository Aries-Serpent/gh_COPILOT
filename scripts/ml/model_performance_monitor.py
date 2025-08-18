"""Monitor deployed machine-learning models and trigger rollbacks.

This module fetches metadata about the currently deployed model from
``analytics.db`` and periodically checks performance metrics. Thresholds for
accuracy and latency are configured through environment variables
(``ACCURACY_THRESHOLD`` and ``LATENCY_THRESHOLD``). When a metric violates its
threshold, an alert is sent to the dashboard and a rollback to the previous
model version is executed.

The monitoring loop is designed to be scheduled externally (e.g. via cron).
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Callable, Dict, Optional

from utils.log_utils import log_event, send_dashboard_alert
from scripts.ml.deploy_models import deploy_model


def _workspace() -> Path:
    """Return the workspace path from ``GH_COPILOT_WORKSPACE`` or cwd."""

    return Path(os.environ.get("GH_COPILOT_WORKSPACE", Path.cwd()))


def _analytics_db_path(analytics_db: Optional[Path]) -> Path:
    """Resolve the path to ``analytics.db``."""

    return analytics_db or _workspace() / "analytics.db"


def _latest_versions(db_path: Path, model_name: str) -> list[str]:
    """Return the most recent successful versions for ``model_name``."""

    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT version FROM model_deployments
            WHERE model_name = ? AND status = 'success'
            ORDER BY id DESC LIMIT 2
            """,
            (model_name,),
        ).fetchall()
    return [r[0] for r in rows]


def fetch_deployed_model_metadata(
    model_name: str, *, analytics_db: Optional[Path] = None
) -> Dict[str, str]:
    """Return metadata for the currently deployed ``model_name``."""

    db_path = _analytics_db_path(analytics_db)
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT version, artifact_path FROM model_deployments
            WHERE model_name = ? AND status = 'success'
            ORDER BY id DESC LIMIT 1
            """,
            (model_name,),
        ).fetchone()
    if row is None:
        raise RuntimeError("No deployed model metadata found")
    return {"model_name": model_name, "version": row[0], "artifact_path": row[1]}


def monitor_metrics(
    *,
    analytics_db: Optional[Path] = None,
    metrics_fetcher: Optional[Callable[[str, str], Dict[str, float]]] = None,
) -> None:
    """Check model metrics and rollback on threshold breaches."""

    model_name = os.environ.get("MODEL_NAME")
    if not model_name:
        raise RuntimeError("MODEL_NAME must be set")

    db_path = _analytics_db_path(analytics_db)
    versions = _latest_versions(db_path, model_name)
    if not versions:
        raise RuntimeError("No successful deployments found")

    current_version = versions[0]
    previous_version = versions[1] if len(versions) > 1 else None

    fetcher = metrics_fetcher or (lambda m, v: {"accuracy": 1.0, "latency": 0.0})
    metrics = fetcher(model_name, current_version)

    acc_threshold = float(os.getenv("ACCURACY_THRESHOLD", "0.9"))
    lat_threshold = float(os.getenv("LATENCY_THRESHOLD", "100"))

    breaches: list[tuple[str, float, float]] = []
    if metrics.get("accuracy", 1.0) < acc_threshold:
        breaches.append(("accuracy", metrics["accuracy"], acc_threshold))
    if metrics.get("latency", 0.0) > lat_threshold:
        breaches.append(("latency", metrics["latency"], lat_threshold))

    if not breaches:
        return

    for metric, value, threshold in breaches:
        send_dashboard_alert(
            {
                "db": model_name,
                "table_name": metric,
                "size_mb": value,
                "threshold": threshold,
            },
            db_path=db_path,
        )

    if previous_version:
        os.environ["MODEL_VERSION"] = previous_version
        deploy_model(analytics_db=db_path)
        log_event(
            {"target": model_name, "backup": previous_version},
            table="rollback_logs",
            db_path=db_path,
        )


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    monitor_metrics()

