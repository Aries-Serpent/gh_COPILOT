from __future__ import annotations

from web_gui.monitoring.performance_metrics import PerformanceMetricsCollector, DictExporter as PerfExporter
from web_gui.monitoring.compliance_monitoring import collect_compliance_metrics
from web_gui.monitoring.quantum_metrics import collect_quantum_metrics


def test_performance_metrics_collector_and_exporter() -> None:
    collector = PerformanceMetricsCollector()
    exporter = PerfExporter()
    metrics = exporter.export(collector.collect())
    assert 0.0 <= metrics["cpu_percent"] <= 100.0
    assert 0.0 <= metrics["memory_percent"] <= 100.0


def test_compliance_metrics_success() -> None:
    metrics = collect_compliance_metrics({"policy": "p", "status": "ok"})
    assert metrics == {"is_compliant": True, "missing": []}


def test_compliance_metrics_missing() -> None:
    metrics = collect_compliance_metrics({})
    assert metrics == {"is_compliant": False, "missing": ["policy", "status"]}


def test_quantum_metrics_average_fallback() -> None:
    metrics = collect_quantum_metrics([1.0, 3.0])
    assert metrics == {"quantum_score": 2.0}
