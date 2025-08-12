import sqlite3
import sys
import types

psutil_stub = types.SimpleNamespace(
    cpu_percent=lambda interval=1: 0.0,
    virtual_memory=lambda: types.SimpleNamespace(percent=0.0),
    disk_usage=lambda path: types.SimpleNamespace(percent=0.0),
    net_io_counters=lambda: types.SimpleNamespace(bytes_sent=0, bytes_recv=0),
)
sys.modules.setdefault("psutil", psutil_stub)


class _IForestStub:
    def __init__(self, contamination=0.1, random_state=None):
        self.contamination = contamination

    def fit(self, data):
        self.data = data

    def predict(self, data):
        threshold = max(max(row) for row in self.data) * 1.5 if self.data else 0
        return [ -1 if max(row) > threshold else 1 for row in data ]

    def score_samples(self, data):
        class _Score(list):
            def __neg__(self):
                return _Score([-x for x in self])

        return _Score([max(row) for row in data])


sklearn_stub = types.SimpleNamespace(
    ensemble=types.SimpleNamespace(IsolationForest=_IForestStub)
)
sys.modules.setdefault("sklearn", sklearn_stub)
sys.modules.setdefault("sklearn.ensemble", sklearn_stub.ensemble)


class _TqdmStub:
    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def update(self, *args, **kwargs):
        pass


sys.modules.setdefault("tqdm", types.SimpleNamespace(tqdm=_TqdmStub))

from monitoring.unified_monitoring_optimization_system import detect_anomalies
from unified_monitoring_optimization_system import (
    push_metrics,
    train_anomaly_model,
    get_anomaly_summary,
)


def test_model_training_persisted(tmp_path):
    db = tmp_path / "analytics.db"
    metrics = {
        "cpu_percent": 0.0,
        "memory_percent": 0.0,
        "disk_percent": 0.0,
        "net_bytes_sent": 0.0,
        "net_bytes_recv": 0.0,
    }
    for _ in range(4):
        push_metrics(metrics, db_path=db)
    version = train_anomaly_model(db_path=db)
    assert version == 1
    with sqlite3.connect(db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM anomaly_models").fetchone()[0]
    assert count == 1


def test_anomaly_summary_retrieval(tmp_path):
    db = tmp_path / "analytics.db"
    normal = {
        "cpu_percent": 0.0,
        "memory_percent": 0.0,
        "disk_percent": 0.0,
        "net_bytes_sent": 0.0,
        "net_bytes_recv": 0.0,
    }
    outlier = {
        "cpu_percent": 100.0,
        "memory_percent": 100.0,
        "disk_percent": 100.0,
        "net_bytes_sent": 100.0,
        "net_bytes_recv": 100.0,
    }
    history = []
    for _ in range(5):
        push_metrics(normal, db_path=db)
        history.append(normal)
    history.append(outlier)
    anomalies = detect_anomalies(history, db_path=db)
    assert anomalies
    summary = get_anomaly_summary(db_path=db)
    assert summary
    assert summary[0]["anomaly_score"] == anomalies[0]["anomaly_score"]
