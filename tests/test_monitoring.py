#!/usr/bin/env python3
import sys

sys.modules.pop("monitoring", None)
sys.modules.pop("monitoring.health_monitor", None)

from monitoring.health_monitor import check_alerts, quantum_hook as health_quantum_hook
from monitoring.performance_tracker import (
    track_query_time,
    record_error,
    quantum_hook as perf_quantum_hook,
)
from monitoring.quantum_score import quantum_score


def test_health_monitor_anomaly_detection():
    metrics = {"cpu_percent": 95.0, "memory_percent": 10.0, "disk_percent": 10.0}
    alerts = check_alerts(metrics)
    expected = quantum_score([metrics["cpu_percent"], metrics["memory_percent"], metrics["disk_percent"]])
    assert alerts["cpu"]
    assert alerts["ml_anomaly"]
    assert metrics["quantum_score"] == expected
    assert health_quantum_hook(metrics) == expected


def test_performance_tracker_alerts(tmp_path):
    db = tmp_path / "analytics.db"
    metrics = track_query_time("slow_query", 150.0, db_path=db)
    assert metrics["response_time_alert"]
    assert metrics["ml_anomaly"]
    assert "quantum_score" in metrics
    metrics = record_error("slow_query", db_path=db)
    expected = quantum_score([metrics["avg_response_time_ms"], metrics["error_rate"] * 100])
    assert metrics["error_rate_alert"]
    assert perf_quantum_hook(metrics) == expected
    assert metrics["quantum_score"] == expected
