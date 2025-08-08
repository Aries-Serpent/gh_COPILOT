from pathlib import Path

from src.monitoring.anomaly import detect_anomalies, train_baseline_models


def _data_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "metrics"


def test_detects_known_anomaly() -> None:
    models = train_baseline_models(_data_dir())
    anomalies = detect_anomalies(models, {"cpu_usage": 25, "memory_usage": 103})
    assert anomalies["cpu_usage"]
    assert not anomalies["memory_usage"]


def test_detects_memory_spike() -> None:
    models = train_baseline_models(_data_dir())
    anomalies = detect_anomalies(models, {"memory_usage": 160})
    assert anomalies["memory_usage"]
