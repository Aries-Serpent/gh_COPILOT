#!/usr/bin/env python3
import sqlite3
from pathlib import Path

from monitoring.health_monitor import (
    ensure_table,
    record_system_health,
    recent_average,
)
import scripts.monitoring.unified_monitoring_optimization_system as umos
from unified_monitoring_optimization_system import collect_metrics


def _prepare_db(tmp_path: Path) -> Path:
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        ensure_table(conn)
    return db


def test_record_system_health_inserts_row(tmp_path, monkeypatch):
    db = _prepare_db(tmp_path)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    metrics = record_system_health(db_path=db)
    assert "cpu_percent" in metrics
    with sqlite3.connect(db) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM system_health")
        assert cur.fetchone()[0] == 1


def test_recent_average_computes_values(tmp_path):
    db = _prepare_db(tmp_path)
    with sqlite3.connect(db) as conn:
        conn.executemany(
            "INSERT INTO system_health (cpu_percent, memory_percent, disk_percent, net_bytes_sent, net_bytes_recv) VALUES (?, ?, ?, ?, ?)",
            [(10, 20, 30, 40, 50), (20, 30, 40, 50, 60)],
        )
        conn.commit()
    avg = recent_average(2, db_path=db)
    assert round(avg["avg_cpu_percent"], 1) == 15.0
    assert round(avg["avg_memory_percent"], 1) == 25.0


def test_collect_metrics_records_session(tmp_path, monkeypatch):
    class DummySession:
        def start_session(self) -> bool:
            return True

    monkeypatch.setattr(umos, "UnifiedSessionManagementSystem", lambda: DummySession())
    monkeypatch.setattr(
        umos,
        "gather_metrics",
        lambda: {
            "cpu_percent": 1.0,
            "memory_percent": 2.0,
            "disk_percent": 3.0,
            "net_bytes_sent": 4,
            "net_bytes_recv": 5,
        },
    )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))

    result = collect_metrics()
    assert result["session_id"]

    with sqlite3.connect(tmp_path / "analytics.db") as conn:
        row = conn.execute(
            "SELECT session_id, cpu_percent FROM monitoring_metrics"
        ).fetchone()
    assert row[0] == result["session_id"]
    assert row[1] == 1.0
