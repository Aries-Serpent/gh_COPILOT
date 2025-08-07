import os
import sqlite3

from unified_monitoring_optimization_system import (
    detect_anomalies,
    push_metrics,
    train_anomaly_model,
)


def test_train_anomaly_model_logs_metadata(tmp_path):
    db_path = tmp_path / "analytics.db"
    model_path = tmp_path / "model.pkl"
    metrics = [
        {"a": 1.0, "b": 1.0},
        {"a": 2.0, "b": 2.0},
        {"a": 1.5, "b": 1.5},
    ]
    for m in metrics:
        push_metrics(m, db_path=db_path)

    version = train_anomaly_model(
        db_path=db_path, model_path=model_path, contamination=0.2
    )
    assert version == 1
    assert model_path.exists()

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT version, model_path, contamination, row_count FROM anomaly_model_metadata"
        ).fetchone()

    assert row == (1, str(model_path), 0.2, len(metrics))


def test_detect_anomalies_retrains_when_stale(tmp_path):
    db_path = tmp_path / "analytics.db"
    model_path = tmp_path / "model.pkl"

    normal = [
        {"a": 1.0, "b": 1.0},
        {"a": 1.1, "b": 1.1},
        {"a": 0.9, "b": 0.9},
    ]
    for m in normal:
        push_metrics(m, db_path=db_path)

    train_anomaly_model(db_path=db_path, model_path=model_path)
    os.utime(model_path, (0, 0))

    history = normal + [{"a": 10.0, "b": 10.0}]
    anomalies = detect_anomalies(
        history,
        db_path=db_path,
        model_path=model_path,
        retrain_interval=1,
    )

    assert anomalies  # anomaly should be detected

    with sqlite3.connect(db_path) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM anomaly_model_metadata"
        ).fetchone()[0]

    assert count == 2

