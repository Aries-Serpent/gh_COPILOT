"""Utilities for the Unified Monitoring Optimization System.

This module re-exports :class:`EnterpriseUtility` and :func:`collect_metrics`
from ``scripts.monitoring.unified_monitoring_optimization_system`` and
provides a ``push_metrics`` helper used by tests and lightweight integrations
to store arbitrary monitoring metrics in ``analytics.db``.  It also exposes
``auto_heal_session`` which couples anomaly detection with the session
management subsystem to restart sessions when system metrics deviate
significantly from learned baselines.
"""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Dict, Iterable, List, Optional, TYPE_CHECKING

import psutil
from sklearn.ensemble import IsolationForest
from scripts.monitoring.unified_monitoring_optimization_system import (
    EnterpriseUtility,
)

try:  # pragma: no cover - optional quantum library
    from quantum_algorithm_library_expansion import quantum_score_stub
except Exception:  # pragma: no cover - library may be missing
    quantum_score_stub = None

WORKSPACE_ROOT = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
DB_PATH = WORKSPACE_ROOT / "databases" / "analytics.db"

__all__ = [
    "EnterpriseUtility",
    "collect_metrics",
    "push_metrics",
    "detect_anomalies",
    "QuantumInterface",
    "auto_heal_session",
    "record_quantum_score",
]

if TYPE_CHECKING:  # pragma: no cover - imported for type hints only
    from scripts.utilities.unified_session_management_system import (
        UnifiedSessionManagementSystem,
    )


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


def collect_metrics(
    *, session_id: Optional[str] = None, db_path: Optional[Path] = None
) -> Dict[str, float]:
    """Collect system metrics and persist them.

    Parameters
    ----------
    session_id:
        Optional identifier to associate metrics with a session.
    db_path:
        Optional database override. Defaults to :data:`DB_PATH`.

    Returns
    -------
    dict
        Mapping of collected metric names to values.
    """

    metrics = {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
        "net_bytes_sent": psutil.net_io_counters().bytes_sent,
        "net_bytes_recv": psutil.net_io_counters().bytes_recv,
    }
    push_metrics(metrics, db_path=db_path, session_id=session_id)
    return metrics


def _train_isolation_forest(
    data: List[List[float]], *, contamination: float
) -> IsolationForest:
    """Train an :class:`IsolationForest` on ``data``.

    Parameters
    ----------
    data:
        Two dimensional list representing metric history.
    contamination:
        Proportion of outliers in the data set.

    Returns
    -------
    IsolationForest
        Fitted model ready for anomaly scoring.
    """

    model = IsolationForest(contamination=contamination, random_state=42)
    model.fit(data)
    return model


def _ensure_anomaly_table(conn: sqlite3.Connection) -> None:
    """Create the ``anomaly_results`` table if required."""

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS anomaly_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            metrics_json TEXT NOT NULL,
            anomaly_score REAL NOT NULL,
            quantum_score REAL,
            composite_score REAL NOT NULL
        )
        """
    )


def detect_anomalies(
    history: Iterable[Dict[str, float]],
    *,
    contamination: float = 0.1,
    db_path: Optional[Path] = None,
) -> List[Dict[str, float]]:
    """Identify anomalous metric entries and persist results.

    The function trains an :class:`IsolationForest` on ``history`` and
    computes anomaly scores for each entry. When the optional
    :func:`quantum_score_stub` is available a composite health metric is
    produced by averaging the anomaly score with the quantum score. All
    detected anomalies are stored in ``analytics.db`` for dashboard
    consumption.

    Parameters
    ----------
    history:
        Iterable of metric mappings ordered chronologically.
    contamination:
        Proportion of outliers in the data set.
    db_path:
        Optional path to the analytics database. Defaults to
        :data:`DB_PATH`.

    Returns
    -------
    list of dict
        Subset of ``history`` flagged as anomalies. Each entry contains the
        additional keys ``anomaly_score``, ``quantum_score`` (when available)
        and ``composite_score``.
    """

    history_list = list(history)
    if not history_list:
        return []

    keys = sorted(history_list[0])
    data = [[m[k] for k in keys] for m in history_list]
    model = _train_isolation_forest(data, contamination=contamination)
    preds = model.predict(data)
    scores = -model.score_samples(data)

    path = db_path or DB_PATH
    anomalies: List[Dict[str, float]] = []

    with sqlite3.connect(path) as conn:
        _ensure_anomaly_table(conn)
        for metrics, pred, score in zip(history_list, preds, scores):
            if pred != -1:
                continue
            anomaly: Dict[str, float] = dict(metrics)
            anomaly_score = float(score)
            anomaly["anomaly_score"] = anomaly_score
            quantum_score = (
                float(quantum_score_stub(metrics.values()))
                if quantum_score_stub is not None
                else None
            )
            if quantum_score is not None:
                anomaly["quantum_score"] = quantum_score
                composite = (anomaly_score + quantum_score) / 2.0
            else:
                composite = anomaly_score
            anomaly["composite_score"] = composite
            anomalies.append(anomaly)
            conn.execute(
                """
                INSERT INTO anomaly_results (
                    metrics_json, anomaly_score, quantum_score, composite_score
                ) VALUES (?, ?, ?, ?)
                """,
                (json.dumps(metrics), anomaly_score, quantum_score, composite),
            )
        conn.commit()

    return anomalies


def record_quantum_score(
    metrics: Dict[str, float], *, db_path: Optional[Path] = None
) -> float:
    """Record a quantum score for ``metrics`` in ``analytics.db``.

    When :func:`quantum_score_stub` is available its output is used. Otherwise
    a deterministic average of the metric values provides a placeholder score.

    Parameters
    ----------
    metrics:
        Mapping of metric names to numeric values.
    db_path:
        Optional analytics database path. Defaults to :data:`DB_PATH`.

    Returns
    -------
    float
        The calculated quantum score.
    """

    score = (
        float(quantum_score_stub(metrics.values()))
        if quantum_score_stub is not None
        else sum(metrics.values()) / len(metrics)
    )
    path = db_path or DB_PATH
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS quantum_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metrics_json TEXT NOT NULL,
                score REAL NOT NULL
            )
            """
        )
        conn.execute(
            "INSERT INTO quantum_scores (metrics_json, score) VALUES (?, ?)",
            (json.dumps(metrics), score),
        )
        conn.commit()
    return score


def auto_heal_session(
    history: Optional[Iterable[Dict[str, float]]] = None,
    *,
    anomalies: Optional[Iterable[Dict[str, float]]] = None,
    contamination: float = 0.1,
    manager: Optional[UnifiedSessionManagementSystem] = None,
    db_path: Optional[Path] = None,
) -> bool:
    """Restart the session when metric anomalies are detected.

    Parameters
    ----------
    history:
        Iterable of metric mappings ordered chronologically. Required when
        ``anomalies`` is not supplied.
    anomalies:
        Pre-computed anomalies from :func:`detect_anomalies`. When provided the
        ``history`` parameter is ignored.
    contamination:
        Proportion of outliers passed to :func:`detect_anomalies` when
        ``history`` is used.
    manager:
        Optional session manager.  When omitted a new
        :class:`scripts.utilities.unified_session_management_system.UnifiedSessionManagementSystem`
        instance is created.
    db_path:
        Optional analytics database path forwarded to
        :func:`detect_anomalies`.

    Returns
    -------
    bool
        ``True`` when a restart was attempted due to detected anomalies.
    """

    if anomalies is None:
        if history is None:
            raise ValueError("history or anomalies must be provided")
        anomalies = detect_anomalies(
            history, contamination=contamination, db_path=db_path
        )
    else:
        anomalies = list(anomalies)
    if not anomalies:
        return False
    if manager is None:
        from scripts.utilities.unified_session_management_system import (
            UnifiedSessionManagementSystem,
        )

        manager = UnifiedSessionManagementSystem()
    try:
        try:
            manager.end_session()
        except Exception:
            pass
        manager.start_session()
        return True
    except Exception:
        return False

class QuantumInterface:
    """Placeholder interface for quantum metric processing."""

    @staticmethod
    def analyze(metrics: Dict[str, float]) -> None:
        """Forward metrics to the quantum hook."""

        from scripts.monitoring.unified_monitoring_optimization_system import (
            quantum_hook as _quantum_hook,
        )

        _quantum_hook(metrics)
