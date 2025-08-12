"""Monitoring package with optional service health helpers."""

from __future__ import annotations

__all__: list[str] = []

try:  # Optional dependency on requests
    from .service_health import check_service, run_health_checks, SERVICES

    __all__ += ["check_service", "run_health_checks", "SERVICES"]
except Exception:  # pragma: no cover - missing optional deps
    pass

from .baseline_anomaly_detector import BaselineAnomalyDetector
from .health_monitor import record_system_health
from .performance_tracker import track_query_time, push_metrics
from .compliance_monitor import check_compliance
from .log_error_notifier import monitor_logs
from .unified_monitoring_optimization_system import (
    anomaly_detection_loop,
    detect_anomalies,
)

__all__ += [
    "BaselineAnomalyDetector",
    "record_system_health",
    "track_query_time",
    "push_metrics",
    "check_compliance",
    "monitor_logs",
    "anomaly_detection_loop",
    "detect_anomalies",
]
