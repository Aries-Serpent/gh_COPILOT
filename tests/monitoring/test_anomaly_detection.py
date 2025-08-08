from pathlib import Path
import sqlite3

from src.monitoring.anomaly import detect_anomalies, train_baseline_models
from src.monitoring.anomaly_detector import detect_anomalies as db_detect_anomalies
from src.monitoring.anomaly_detector import train_models as db_train_models


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


def _create_db(db_path: Path) -> Path:
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE sync_metrics(metric TEXT, value REAL)")
    conn.executemany(
        "INSERT INTO sync_metrics(metric, value) VALUES (?, ?)",
        [
            ("cpu_usage", 10.0),
            ("cpu_usage", 12.0),
            ("cpu_usage", 11.0),
            ("memory_usage", 100.0),
            ("memory_usage", 98.0),
            ("memory_usage", 102.0),
        ],
    )
    conn.commit()
    conn.close()
    return db_path


def test_db_detects_known_anomaly(tmp_path: Path) -> None:
    db_file = _create_db(tmp_path / "analytics.db")
    models = db_train_models(db_file)
    anomalies = db_detect_anomalies({"cpu_usage": 25, "memory_usage": 103}, models)
    assert anomalies["cpu_usage"]
    assert not anomalies["memory_usage"]


def test_db_detects_memory_spike(tmp_path: Path) -> None:
    db_file = _create_db(tmp_path / "analytics.db")
    models = db_train_models(db_file)
    anomalies = db_detect_anomalies({"memory_usage": 160}, models)
    assert anomalies["memory_usage"]
