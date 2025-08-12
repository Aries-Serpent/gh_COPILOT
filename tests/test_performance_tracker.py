#!/usr/bin/env python3
import sqlite3
from pathlib import Path

from ghc_monitoring.performance_tracker import benchmark_queries, ensure_table, record_error, track_query_time


def _prepare_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "analytics.db"
    with sqlite3.connect(db_path) as conn:
        ensure_table(conn)
    return db_path


def test_track_query_time_records_and_computes(tmp_path, monkeypatch):
    db = _prepare_db(tmp_path)
    metrics = track_query_time("q1", 40.0, db_path=db)
    assert metrics["avg_response_time_ms"] == 40.0
    assert metrics["error_rate"] == 0.0
    assert not metrics["response_time_alert"]


def test_record_error_updates_error_rate(tmp_path, monkeypatch):
    db = _prepare_db(tmp_path)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    track_query_time("q1", 40.0, db_path=db)
    metrics = record_error("q1", db_path=db)
    assert metrics["error_rate"] == 0.5


def test_benchmark_queries(tmp_path, monkeypatch):
    db = _prepare_db(tmp_path)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    metrics = benchmark_queries(["SELECT COUNT(*) FROM query_performance"], db_path=db)
    assert metrics["within_time_target"]
    assert not metrics["error_rate_alert"]
