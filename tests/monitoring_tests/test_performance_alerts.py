from __future__ import annotations

import asyncio
import sqlite3
import sys
import types
from pathlib import Path

q_stub = types.ModuleType("quantum_algorithm_library_expansion")
q_stub.quantum_score_stub = lambda values: float(sum(values))
sys.modules["quantum_algorithm_library_expansion"] = q_stub
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.modules.pop("monitoring", None)
import monitoring.performance_tracker as pt


def test_alert_thresholds(monkeypatch, tmp_path) -> None:
    db = tmp_path / "metrics.db"
    conn = sqlite3.connect(db)
    monkeypatch.setenv("WEB_DASHBOARD_ENABLED", "1")
    pt.WEB_DASHBOARD_ENABLED = True
    called: dict[str, dict] = {}
    monkeypatch.setattr(pt.logger, "info", lambda msg, m: called.setdefault("metrics", m))

    for _ in range(5):
        pt.track_query_time("q", pt.RESPONSE_TIME_ALERT_MS + 10, db_path=db, conn=conn, commit=False)
    for _ in range(6):
        metrics = pt.record_error("q", db_path=db, conn=conn, commit=False)
    conn.commit()

    assert metrics["response_time_alert"] is True
    assert metrics["error_rate_alert"] is True
    assert "metrics" in called


def test_async_benchmarks(tmp_path) -> None:
    db = tmp_path / "bench.db"
    queries = [
        "CREATE TABLE t(x INTEGER)",
        "INSERT INTO t VALUES (1)",
        "BAD QUERY",
    ]
    metrics = asyncio.run(pt.benchmark_queries_async(queries, db_path=db))
    assert "avg_response_time_ms" in metrics
    avg_overhead = asyncio.run(pt.benchmark_metric_overhead(5, db_path=db))
    assert avg_overhead > 0


def test_track_and_error_without_connection(tmp_path) -> None:
    db = tmp_path / "simple.db"
    metrics = pt.track_query_time("q", 5.0, db_path=db)
    metrics = pt.record_error("q", db_path=db)
    assert metrics["error_rate"] > 0


def test_commit_with_connection(tmp_path) -> None:
    db = tmp_path / "conn.db"
    conn = sqlite3.connect(db)
    pt.track_query_time("q", 1.0, db_path=db, conn=conn)
    metrics = pt.record_error("q", db_path=db, conn=conn)
    assert metrics["error_rate"] > 0
