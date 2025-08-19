"""Utility helpers for metric collection and anomaly detection.

This module provides small, dependency-free helpers for aggregating
metrics from multiple sources and running detector callables. Any
exceptions raised by sources or detectors are logged and captured in
the returned data structures so callers receive best-effort results
without losing diagnostic information.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Iterable, List

logger = logging.getLogger(__name__)


def collect_metrics(sources: Dict[str, Callable[[], Dict[str, Any]]]) -> Dict[str, Any]:
    """Collect metrics from a mapping of ``sources``.

    Each callable in ``sources`` is executed and its return value stored
    under the associated key. If a source raises an exception the error
    is logged and an ``{"error": ...}`` dictionary is recorded instead.
    """

    out: Dict[str, Any] = {}
    for name, fn in sources.items():
        try:
            out[name] = fn()
        except Exception as exc:  # pragma: no cover - best effort logging
            logger.error("metric source %s failed: %s", name, exc)
            out[name] = {"error": str(exc)}
    return out


def detect_anomalies(
    metrics: Dict[str, Any],
    detectors: Iterable[Callable[[Dict[str, Any]], Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    """Run ``detectors`` over ``metrics`` and collect anomaly results."""

    results: List[Dict[str, Any]] = []
    for det in detectors:
        try:
            results.append(det(metrics))
        except Exception as exc:  # pragma: no cover - best effort logging
            name = getattr(det, "__name__", "unknown")
            logger.error("anomaly detector %s failed: %s", name, exc)
            results.append({"detector": name, "error": str(exc)})
    return results


def collect_and_detect(
    sources: Dict[str, Callable[[], Dict[str, Any]]],
    detectors: Iterable[Callable[[Dict[str, Any]], Dict[str, Any]]],
) -> Dict[str, Any]:
    """Collect metrics and immediately run anomaly detectors."""

    metrics = collect_metrics(sources)
    anomalies = detect_anomalies(metrics, detectors)
    return {"metrics": metrics, "anomalies": anomalies}


__all__ = ["collect_metrics", "detect_anomalies", "collect_and_detect"]
