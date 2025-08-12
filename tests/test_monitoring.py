#!/usr/bin/env python3
from ghc_monitoring.health_monitor import check_alerts, quantum_hook as health_quantum_hook
from ghc_monitoring.performance_tracker import (
    track_query_time,
    record_error,
    quantum_hook as perf_quantum_hook,
)


def test_health_monitor_anomaly_detection():
    metrics = {"cpu_percent": 95.0, "memory_percent": 10.0, "disk_percent": 10.0}
    alerts = check_alerts(metrics)
    assert alerts["cpu"]
    assert alerts["ml_anomaly"]
    assert isinstance(health_quantum_hook(metrics), float)


def test_performance_tracker_alerts(tmp_path):
    db = tmp_path / "analytics.db"
    metrics = track_query_time("slow_query", 150.0, db_path=db)
    assert metrics["response_time_alert"]
    assert metrics["ml_anomaly"]
    assert "quantum_score" in metrics
    metrics = record_error("slow_query", db_path=db)
    assert metrics["error_rate_alert"]
    assert isinstance(perf_quantum_hook(metrics), float)
    assert "quantum_score" in metrics
