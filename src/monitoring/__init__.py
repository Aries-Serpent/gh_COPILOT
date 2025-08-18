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

try:  # Optional dependency on psutil via health_monitor
    from .health_monitor import record_system_health  # noqa: F401

    __all__.append("record_system_health")
except Exception:  # pragma: no cover - missing optional deps
    pass

try:  # Optional dependency on numpy via performance_tracker
    from .performance_tracker import track_query_time, push_metrics  # noqa: F401

    __all__ += ["track_query_time", "push_metrics"]
except Exception:  # pragma: no cover - missing optional deps
    pass

try:
    from .compliance_monitor import check_compliance  # noqa: F401

    __all__.append("check_compliance")
except Exception:  # pragma: no cover - missing optional deps
    pass

try:
    from .log_error_notifier import monitor_logs  # noqa: F401

    __all__.append("monitor_logs")
except Exception:  # pragma: no cover - missing optional deps
    pass

def anomaly_detection_loop(*args, **kwargs):
    from unified_monitoring_optimization_system import (  # type: ignore
        anomaly_detection_loop as _loop,
    )

    return _loop(*args, **kwargs)


def detect_anomalies(*args, **kwargs):
    from unified_monitoring_optimization_system import (  # type: ignore
        detect_anomalies as _detect,
    )

    return _detect(*args, **kwargs)


__all__ += ["anomaly_detection_loop", "detect_anomalies"]

