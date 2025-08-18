import sqlite3
import threading
from pathlib import Path
from time import perf_counter, sleep

import sys
import types
import builtins

q_stub = types.ModuleType("quantum_algorithm_library_expansion")

def _quantum_score_stub(values):
    return float(sum(values))

q_stub.quantum_score_stub = _quantum_score_stub
sys.modules["quantum_algorithm_library_expansion"] = q_stub
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.modules.pop("monitoring", None)
import monitoring.performance_tracker as pt


def test_alerting_and_dashboard(monkeypatch, tmp_path) -> None:
    db = tmp_path / "metrics.db"
    conn = sqlite3.connect(db)
    monkeypatch.setenv("WEB_DASHBOARD_ENABLED", "1")
    pt.WEB_DASHBOARD_ENABLED = True
    called = {}
    monkeypatch.setattr(pt.logger, "info", lambda msg, m: called.setdefault("metrics", m))

    for _ in range(5):
        pt.track_query_time("q", pt.RESPONSE_TIME_ALERT_MS + 10, db_path=db, conn=conn, commit=False)
    for _ in range(6):
        metrics = pt.record_error("q", db_path=db, conn=conn, commit=False)
    conn.commit()

    assert metrics["response_time_alert"] is True
    assert metrics["error_rate_alert"] is True
    assert "metrics" in called


def test_ml_and_quantum() -> None:
    metrics = {"avg_response_time_ms": 200.0, "error_rate": 0.5}
    assert pt.ml_anomaly_detect(metrics) is True
    pt.quantum_hook(metrics)
    assert "quantum_score" in metrics


def test_benchmark_and_push_metrics(tmp_path) -> None:
    db = tmp_path / "bench.db"
    queries = [
        "CREATE TABLE t(x INTEGER)",
        "INSERT INTO t VALUES (1)",
        "BAD QUERY",
    ]
    metrics = pt.benchmark_queries(queries, db_path=db)
    assert "avg_response_time_ms" in metrics
    summary = pt.push_metrics(db_path=db)
    assert "error_rate" in summary
    with sqlite3.connect(db) as conn:
        pt.ensure_table(conn)
        count = conn.execute("SELECT COUNT(*) FROM performance_summary").fetchone()[0]
    assert count >= 1


def test_schedule_metrics_push(tmp_path) -> None:
    db = tmp_path / "sched.db"
    stop = threading.Event()
    thread = pt.schedule_metrics_push(0.01, db_path=db, stop_event=stop)
    sleep(0.05)
    stop.set()
    thread.join(timeout=1)
    with sqlite3.connect(db) as conn:
        conn.execute("SELECT COUNT(*) FROM performance_summary").fetchone()


def test_high_frequency_metric_ingestion(tmp_path) -> None:
    db = tmp_path / "load.db"
    conn = sqlite3.connect(db)
    start = perf_counter()
    for i in range(200):
        pt.track_query_time(f"q{i}", 1.0, db_path=db, conn=conn, commit=False)
    duration = perf_counter() - start
    assert duration < 2.0
    metrics = pt.track_query_time("final", 1.0, db_path=db, conn=conn, commit=False)
    conn.commit()
    assert metrics["error_rate"] == 0


def test_benchmark_exported() -> None:
    assert hasattr(builtins, "benchmark_queries")
