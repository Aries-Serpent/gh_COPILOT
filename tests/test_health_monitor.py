#!/usr/bin/env python3
import sqlite3
from pathlib import Path

from ghc_monitoring.health_monitor import (
    ensure_table,
    record_system_health,
    recent_average,
    check_alerts,
)


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
    assert "quantum_score" in metrics
    with sqlite3.connect(db) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM system_health")
        assert cur.fetchone()[0] == 1


def test_recent_average_computes_values(tmp_path):
    db = _prepare_db(tmp_path)
    with sqlite3.connect(db) as conn:
        conn.executemany(
            "INSERT INTO system_health (cpu_percent, memory_percent, disk_percent, net_bytes_sent, net_bytes_recv, quantum_score) VALUES (?, ?, ?, ?, ?, ?)",
            [(10, 20, 30, 40, 50, 0.5), (20, 30, 40, 50, 60, 0.6)],
        )
        conn.commit()
    avg = recent_average(2, db_path=db)
    assert round(avg["avg_cpu_percent"], 1) == 15.0
    assert round(avg["avg_memory_percent"], 1) == 25.0
    assert "avg_quantum_score" in avg


def test_check_alerts_flags_thresholds():
    metrics = {"cpu_percent": 90.0, "memory_percent": 95.0, "disk_percent": 50.0}
    alerts = check_alerts(metrics)
    assert alerts["cpu"] and alerts["memory"]
    assert not alerts["disk"]
