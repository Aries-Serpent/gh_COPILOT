"""Monitoring package with optional service health helpers."""

from __future__ import annotations

__all__: list[str] = []

try:  # Optional dependency on requests
    from .service_health import check_service, run_health_checks, SERVICES

    __all__ += ["check_service", "run_health_checks", "SERVICES"]
except Exception:  # pragma: no cover - missing optional deps
    pass

from .baseline_anomaly_detector import BaselineAnomalyDetector  # noqa: F401

__all__.append("BaselineAnomalyDetector")
