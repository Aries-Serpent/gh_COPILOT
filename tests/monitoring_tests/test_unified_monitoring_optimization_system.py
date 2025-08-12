import json
import sqlite3

import pytest

from ghc_monitoring import detect_anomalies
from unified_monitoring_optimization_system import (
    _ensure_table,
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
            "SELECT version, contamination, row_count FROM anomaly_models"
        ).fetchone()

    assert row == (1, 0.2, len(metrics))


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
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "UPDATE anomaly_models SET trained_at = ? WHERE version = 1",
            ("1970-01-01T00:00:00",),
        )
        conn.commit()

    history = normal + [{"a": 10.0, "b": 10.0}]
    detect_anomalies(
        history,
        db_path=db_path,
        model_path=model_path,
        retrain_interval=1,
    )

    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM anomaly_models").fetchone()[0]

    assert count == 2


def test_push_metrics_rejects_invalid_table(tmp_path):
    db_path = tmp_path / "analytics.db"
    with pytest.raises(ValueError):
        push_metrics({"cpu": 1.0}, table="bad name", db_path=db_path)


def test_valid_table_allows_insert(tmp_path):
    db_path = tmp_path / "analytics.db"
    push_metrics({"cpu": 1.0}, table="valid_table", db_path=db_path)
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT metrics_json FROM valid_table").fetchone()
    assert json.loads(row[0]) == {"cpu": 1.0}


def test_ensure_table_validates_name(tmp_path):
    db_path = tmp_path / "analytics.db"
    with sqlite3.connect(db_path) as conn:
        with pytest.raises(ValueError):
            _ensure_table(conn, "invalid name", False)

