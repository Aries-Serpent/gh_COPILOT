#!/usr/bin/env python3
import sqlite3
from pathlib import Path

import sys

sys.modules.pop("monitoring", None)
sys.modules.pop("monitoring.health_monitor", None)

from monitoring.health_monitor import (
    ensure_table,
    record_system_health,
    recent_average,
    check_alerts,
)
from monitoring import health_monitor as hm
from monitoring.quantum_score import quantum_score


def _prepare_db(tmp_path: Path) -> Path:
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        ensure_table(conn)
    return db


def test_record_system_health_inserts_row(tmp_path, monkeypatch):
    db = _prepare_db(tmp_path)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setattr(hm, "gather_metrics", lambda: {
        "cpu_percent": 10.0,
        "memory_percent": 20.0,
        "disk_percent": 30.0,
        "net_bytes_sent": 40,
        "net_bytes_recv": 50,
    })
    metrics = record_system_health(db_path=db)
    expected = quantum_score([10.0, 20.0, 30.0])
    assert metrics["quantum_score"] == expected
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
    expected = quantum_score([90.0, 95.0, 50.0])
    assert metrics["quantum_score"] == expected
    assert alerts["cpu"] and alerts["memory"]
    assert not alerts["disk"]
