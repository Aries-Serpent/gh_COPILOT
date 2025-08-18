from scripts.monitoring.performance_monitor import (
    collect_cpu_usage,
    collect_memory_usage,
    format_prometheus,
)


def test_collectors_return_values() -> None:
    cpu = collect_cpu_usage()
    mem = collect_memory_usage()
    assert 0 <= cpu <= 100
    assert 0 <= mem <= 100


def test_format_prometheus() -> None:
    text = format_prometheus({"cpu_usage_percent": 1.0, "memory_usage_percent": 2.0})
    assert "cpu_usage_percent" in text
    assert "memory_usage_percent" in text

