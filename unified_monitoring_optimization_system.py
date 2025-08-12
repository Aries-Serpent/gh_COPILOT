"""Utilities for the Unified Monitoring Optimization System.

This module re-exports :class:`EnterpriseUtility` and :func:`collect_metrics`
from ``scripts.monitoring.unified_monitoring_optimization_system`` and
provides a ``push_metrics`` helper used by tests and lightweight integrations
to store arbitrary monitoring metrics in ``analytics.db``. Table names supplied
to ``push_metrics`` are validated to contain only alphanumeric characters and
underscores to prevent SQL injection.  It also exposes ``auto_heal_session``
which couples anomaly detection with the session management subsystem to
restart sessions when system metrics deviate significantly from learned
baselines.
"""

from __future__ import annotations

import json
import os
import pickle
import sqlite3
import time
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, TYPE_CHECKING, Any

from types import SimpleNamespace

try:  # pragma: no cover - optional dependency
    import psutil  # type: ignore
except Exception:  # pragma: no cover - provide stub
    psutil = SimpleNamespace(
        cpu_percent=lambda interval=0: 0.0,
        virtual_memory=lambda: SimpleNamespace(percent=0.0),
        disk_usage=lambda _p: SimpleNamespace(percent=0.0),
        net_io_counters=lambda: SimpleNamespace(bytes_sent=0, bytes_recv=0),
    )
try:  # pragma: no cover - optional ML dependency
    from sklearn.ensemble import IsolationForest  # type: ignore
except Exception:  # pragma: no cover - stub when sklearn missing
    IsolationForest = None  # type: ignore[assignment]
try:  # pragma: no cover - optional dependency chain
    from scripts.monitoring.unified_monitoring_optimization_system import (
        EnterpriseUtility,  # type: ignore
    )
except Exception:  # pragma: no cover - provide stub when deps missing
    class EnterpriseUtility:  # type: ignore[empty-body]
        """Fallback stub used when the monitoring utilities are unavailable."""

        pass

try:  # pragma: no cover - optional quantum library
    from quantum_algorithm_library_expansion import quantum_score_stub
except Exception:  # pragma: no cover - library may be missing
    quantum_score_stub = None

WORKSPACE_ROOT = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
DB_PATH = WORKSPACE_ROOT / "databases" / "analytics.db"
MODEL_PATH = WORKSPACE_ROOT / "artifacts" / "anomaly_iforest.pkl"
WEB_DASHBOARD_ENABLED = os.getenv("WEB_DASHBOARD_ENABLED") == "1"
logger = logging.getLogger(__name__)


def _update_dashboard(payload: Dict[str, float]) -> None:
    """Emit payload to the dashboard when enabled."""

    if WEB_DASHBOARD_ENABLED:
        logger.info("[DASHBOARD] %s", payload)

__all__ = [
    "EnterpriseUtility",
    "collect_metrics",
    "push_metrics",
    "train_anomaly_model",
    "detect_anomalies",
    "get_anomaly_summary",
    "QuantumInterface",
    "auto_heal_session",
    "anomaly_detection_loop",
    "record_quantum_score",
]

_TABLE_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _validate_table_name(table: str) -> str:
    """Ensure ``table`` is a safe SQLite identifier."""

    if not _TABLE_NAME_RE.match(table):
        raise ValueError(f"invalid table name: {table!r}")
    return table

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

    table = _validate_table_name(table)

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

    table = _validate_table_name(table)
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
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    if count >= 5:
        try:
            train_anomaly_model(db_path=path)
        except Exception:
            pass


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
) -> Any:
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

    if IsolationForest is None:
        return None
    model = IsolationForest(contamination=contamination, random_state=42)
    model.fit(data)
    return model


def train_anomaly_model(
    *,
    db_path: Optional[Path] = None,
    model_path: Optional[Path] = None,
    contamination: float = 0.1,
    limit: int = 100,
) -> Optional[int]:
    """Fit an :class:`IsolationForest` using historical metrics.

    Metrics are read from the ``monitoring_metrics`` table in ``analytics.db``.
    The fitted model along with the feature ordering is persisted to the
    ``anomaly_models`` table and optionally to ``model_path`` for backwards
    compatibility.

    Parameters
    ----------
    db_path:
        Optional path to the analytics database. Defaults to :data:`DB_PATH`.
    model_path:
        Optional path where the trained model is also persisted as a pickle
        file. Defaults to :data:`MODEL_PATH`.
    contamination:
        Proportion of outliers expected in the historical data.
    limit:
        Maximum number of recent metric rows used for training. Older entries
        are ignored.

    Returns
    -------
    Optional[int]
        The version number of the persisted model or ``None`` when no
        historical metrics were available for training.
    """

    db_file = db_path or DB_PATH
    model_file = model_path or MODEL_PATH

    with sqlite3.connect(db_file) as conn:
        try:
            rows = conn.execute(
                "SELECT metrics_json FROM monitoring_metrics ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        except sqlite3.Error:
            return None
    if not rows:
        return None

    # restore chronological order
    metrics_list = [json.loads(row[0]) for row in reversed(rows)]
    keys = sorted(metrics_list[0])
    data = [[m[k] for k in keys] for m in metrics_list]
    model = _train_isolation_forest(data, contamination=contamination)

    payload = {"model": model, "keys": keys}

    model_file.parent.mkdir(parents=True, exist_ok=True)
    with open(model_file, "wb") as fh:
        pickle.dump(payload, fh)

    blob = pickle.dumps(payload)
    with sqlite3.connect(db_file) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS anomaly_models (
                version INTEGER PRIMARY KEY AUTOINCREMENT,
                trained_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                model BLOB NOT NULL,
                contamination REAL NOT NULL,
                row_count INTEGER NOT NULL
            )
            """
        )
        conn.execute(
            "INSERT INTO anomaly_models (model, contamination, row_count) VALUES (?, ?, ?)",
            (blob, contamination, len(data)),
        )
        conn.commit()
        version = conn.execute(
            "SELECT MAX(version) FROM anomaly_models"
        ).fetchone()[0]
    return int(version)


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
    model_path: Optional[Path] = None,
    retrain_interval: float = 3600,
) -> List[Dict[str, float]]:
    """Identify anomalous metric entries and persist results.

    The function loads a persisted :class:`IsolationForest` model from
    ``analytics.db``, training it periodically from recent historical metrics
    stored in ``analytics.db``. It then computes anomaly scores for ``history``
    using this model. When the optional :func:`quantum_score_stub` is available
    a composite health metric is produced by averaging the anomaly score with
    the quantum score. All detected anomalies are stored in ``analytics.db``
    for dashboard consumption.

    Parameters
    ----------
    history:
        Iterable of metric mappings ordered chronologically.
    contamination:
        Proportion of outliers in the data set.
    db_path:
        Optional path to the analytics database. Defaults to
        :data:`DB_PATH`.
    model_path:
        Optional path to the persisted model. Defaults to
        :data:`MODEL_PATH`.
    retrain_interval:
        Seconds after which the model is retrained using historical metrics.

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

    db_file = db_path or DB_PATH
    model_file = model_path or MODEL_PATH

    payload = None
    with sqlite3.connect(db_file) as conn:
        row = conn.execute(
            "SELECT trained_at, model FROM anomaly_models ORDER BY version DESC LIMIT 1"
        ).fetchone()
    if row:
        trained_at = datetime.fromisoformat(row[0])
        age = time.time() - trained_at.timestamp()
        if age > retrain_interval:
            row = None
    if row is None:
        train_anomaly_model(
            db_path=db_file, model_path=model_file, contamination=contamination
        )
        with sqlite3.connect(db_file) as conn:
            row = conn.execute(
                "SELECT trained_at, model FROM anomaly_models ORDER BY version DESC LIMIT 1"
            ).fetchone()
    if row:
        payload = pickle.loads(row[1])

    if payload is not None:
        model = payload["model"]
        keys = payload["keys"]
        data = [[m.get(k, 0.0) for k in keys] for m in history_list]
    else:
        keys = sorted(history_list[0])
        data = [[m[k] for k in keys] for m in history_list]
        model = _train_isolation_forest(data, contamination=contamination)

    preds = model.predict(data)
    scores = -model.score_samples(data)

    anomalies: List[Dict[str, float]] = []

    with sqlite3.connect(db_file) as conn:
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
            _update_dashboard(anomaly)
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


def get_anomaly_summary(
    *, limit: int = 10, db_path: Optional[Path] = None
) -> List[Dict[str, float]]:
    """Return recent anomaly scores from ``analytics.db``.

    Parameters
    ----------
    limit:
        Maximum number of recent anomaly rows to return.
    db_path:
        Optional path to the analytics database. Defaults to :data:`DB_PATH`.

    Returns
    -------
    list of dict
        Each entry contains ``timestamp`` and ``anomaly_score``.
    """

    db_file = db_path or DB_PATH
    if not db_file.exists():
        return []
    with sqlite3.connect(db_file) as conn:
        rows = conn.execute(
            "SELECT timestamp, anomaly_score FROM anomaly_results ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [
        {"timestamp": row[0], "anomaly_score": float(row[1])} for row in rows
    ]


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
    _update_dashboard({"quantum_score": score})
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


def anomaly_detection_loop(
    interval: float = 5.0,
    *,
    iterations: Optional[int] = None,
    contamination: float = 0.1,
    threshold: float = 0.5,
    manager: Optional[UnifiedSessionManagementSystem] = None,
    db_path: Optional[Path] = None,
    model_path: Optional[Path] = None,
    collector=collect_metrics,
) -> None:
    """Continuously collect metrics and restart sessions on anomalies.

    Parameters
    ----------
    interval:
        Seconds to wait between metric collections.
    iterations:
        Optional maximum number of iterations. ``None`` runs indefinitely.
    contamination:
        Proportion of outliers passed to :func:`detect_anomalies`.
    manager:
        Optional session manager instance used by :func:`auto_heal_session`.
    db_path:
        Optional analytics database path forwarded to collectors and detectors.
    model_path:
        Optional persisted model path forwarded to :func:`detect_anomalies`.
    collector:
        Metric collection callable. Defaults to :func:`collect_metrics`.
    """

    history: List[Dict[str, float]] = []
    count = 0
    while iterations is None or count < iterations:
        metrics = collector(db_path=db_path)
        history.append(metrics)
        anomalies = detect_anomalies(
            history,
            contamination=contamination,
            db_path=db_path,
            model_path=model_path,
        )
        filtered = [
            a for a in anomalies if a.get("anomaly_score", 0) > threshold
        ]
        if filtered:
            auto_heal_session(
                anomalies=filtered, manager=manager, db_path=db_path
            )
        count += 1
        if iterations is None or count < iterations:
            time.sleep(interval)

class QuantumInterface:
    """Concrete interface for quantum metric processing."""

    @staticmethod
    def analyze(
        metrics: Dict[str, float], *, db_path: Optional[Path] = None
    ) -> float:
        """Record and return a quantum score for ``metrics``."""

        score = record_quantum_score(metrics, db_path=db_path)
        metrics["quantum_score"] = score
        return score
