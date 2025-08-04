"""Utilities for the Unified Monitoring Optimization System.

This module exposes :class:`EnterpriseUtility` from
``scripts.monitoring.unified_monitoring_optimization_system`` and provides a
``push_metrics`` helper used by tests and lightweight integrations to store
arbitrary monitoring metrics in ``analytics.db``.
"""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from sklearn.ensemble import IsolationForest

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from scripts.monitoring.unified_monitoring_optimization_system import (
        EnterpriseUtility as _EnterpriseUtility,  # noqa: F401
        collect_metrics as _collect_metrics,  # noqa: F401
    )
else:
    from scripts.monitoring.unified_monitoring_optimization_system import (
        collect_metrics,
    )

WORKSPACE_ROOT = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
DB_PATH = WORKSPACE_ROOT / "databases" / "analytics.db"

__all__ = [
    "push_metrics",
    "detect_anomalies",
    "QuantumInterface",
    "collect_metrics",
]


def _ensure_table(conn: sqlite3.Connection, table: str, with_session: bool) -> None:
    """Create a table for pushed metrics if it does not exist.

    Parameters
    ----------
    conn:
        Open SQLite connection.
    table:
        Name of the metrics table.
    with_session:
        When ``True`` the table includes a ``session_id`` column linked to
        ``unified_wrapup_sessions``.
    """

    if with_session:
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metrics_json TEXT NOT NULL,
                FOREIGN KEY(session_id) REFERENCES unified_wrapup_sessions(session_id)
            )
            """
        )
    else:
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metrics_json TEXT NOT NULL
            )
            """
        )


def push_metrics(
    metrics: Dict[str, float],
    *,
    table: str = "monitoring_metrics",
    db_path: Optional[Path] = None,
    session_id: Optional[str] = None,
) -> None:
    """Store ``metrics`` in ``analytics.db``.

    When ``session_id`` is provided the metrics row is linked to the
    ``unified_wrapup_sessions`` table, enabling correlation with session
    lifecycle data.

    Parameters
    ----------
    metrics:
        Mapping of metric names to numeric values.
    table:
        Optional table name. Defaults to ``monitoring_metrics``.
    db_path:
        Optional path to the analytics database. If omitted the database in
        ``GH_COPILOT_WORKSPACE`` is used.
    session_id:
        Optional session identifier to associate metrics with a lifecycle
        entry.
    """

    path = db_path or DB_PATH
    with sqlite3.connect(path) as conn:
        _ensure_table(conn, table, session_id is not None)
        if session_id is None:
            conn.execute(
                f"INSERT INTO {table} (metrics_json) VALUES (?)",
                (json.dumps(metrics),),
            )
        else:
            conn.execute(
                f"INSERT INTO {table} (session_id, metrics_json) VALUES (?, ?)",
                (session_id, json.dumps(metrics)),
            )
        conn.commit()


def detect_anomalies(
    history: Iterable[Dict[str, float]], *, contamination: float = 0.1
) -> List[Dict[str, float]]:
    """Identify anomalous metric entries using ``IsolationForest``.

    Parameters
    ----------
    history:
        Iterable of metric mappings ordered chronologically.
    contamination:
        Proportion of outliers in the data set.

    Returns
    -------
    list of dict
        Subset of ``history`` flagged as anomalies.
    """

    history_list = list(history)
    if not history_list:
        return []

    keys = sorted(history_list[0])
    data = [[m[k] for k in keys] for m in history_list]
    model = IsolationForest(contamination=contamination, random_state=42)
    preds = model.fit_predict(data)
    return [m for m, pred in zip(history_list, preds) if pred == -1]


class QuantumInterface:
    """Placeholder interface for quantum metric processing."""

    @staticmethod
    def analyze(metrics: Dict[str, float]) -> None:
        """Forward metrics to the quantum hook."""

        from scripts.monitoring.unified_monitoring_optimization_system import (
            quantum_hook as _quantum_hook,
        )

        _quantum_hook(metrics)
