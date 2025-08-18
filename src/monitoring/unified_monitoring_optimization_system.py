"""Lightweight re-exports for monitoring utilities.

This module exposes the anomaly detection helpers from
``unified_monitoring_optimization_system`` inside the ``monitoring`` package.
It provides a thin wrapper around :func:`detect_anomalies` and
:func:`anomaly_detection_loop` so consumers can import them using
``from monitoring.unified_monitoring_optimization_system import ...``.

Only the two public helpers are exported via ``__all__``; other functions are
re-exported solely for test purposes.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import importlib

_core = importlib.import_module("unified_monitoring_optimization_system")
_auto_heal_session = _core.auto_heal_session
_collect_metrics = _core.collect_metrics
_detect_impl = _core.detect_anomalies
_register_hook = _core.register_hook
push_metrics = _core.push_metrics  # noqa: F401 - re-exported for tests
train_anomaly_model = _core.train_anomaly_model  # noqa: F401 - re-exported for tests

# Exported public helpers
__all__ = ["anomaly_detection_loop", "detect_anomalies", "register_hook"]

# re-exported for tests that patch these callables
collect_metrics = _collect_metrics
auto_heal_session = _auto_heal_session
register_hook = _register_hook


def detect_anomalies(
    history: Iterable[Dict[str, float]],
    *,
    contamination: float = 0.1,
    db_path: Optional[Path] = None,
    model_path: Optional[Path] = None,
    retrain_interval: float = 3600,
) -> List[Dict[str, float]]:
    """Delegate to the core implementation."""

    return _detect_impl(
        history,
        contamination=contamination,
        db_path=db_path,
        model_path=model_path,
        retrain_interval=retrain_interval,
    )


def anomaly_detection_loop(
    interval: float = 5.0,
    *,
    iterations: Optional[int] = None,
    contamination: float = 0.1,
    threshold: float = 0.5,
    manager=None,
    db_path: Optional[Path] = None,
    model_path: Optional[Path] = None,
    collector=collect_metrics,
) -> None:
    """Continuously collect metrics and restart sessions on anomalies."""

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
        filtered = [a for a in anomalies if a.get("anomaly_score", 0) > threshold]
        if filtered:
            auto_heal_session(anomalies=filtered, manager=manager, db_path=db_path)
        count += 1
        if iterations is None or count < iterations:
            time.sleep(interval)


