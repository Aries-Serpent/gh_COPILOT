#!/usr/bin/env python3
import shutil
import sqlite3
from pathlib import Path

from archive.consolidated_scripts.unified_monitoring_optimization_system import EnterpriseUtility
import logging


def test_perform_utility_function_inserts_metrics(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[1]
    workspace = tmp_path
    db_dir = workspace / "databases"
    db_dir.mkdir()
    perf_db = db_dir / "performance_monitoring.db"
    opt_db = db_dir / "optimization_metrics.db"
    with sqlite3.connect(perf_db) as conn:
        conn.execute(
            "CREATE TABLE performance_metrics (cpu_percent REAL, memory_percent REAL, disk_usage_percent REAL, network_io_bytes REAL)"
        )
        conn.execute("INSERT INTO performance_metrics VALUES (10, 20, 30, 40)")
    with sqlite3.connect(opt_db) as conn:
        conn.execute(
            "CREATE TABLE optimization_metrics (session_id TEXT, timestamp TEXT, performance_delta REAL, cpu_usage REAL, memory_usage REAL, disk_io REAL, metrics_json TEXT)"
        )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))

    util = EnterpriseUtility(workspace_path=str(workspace))
    assert util.perform_utility_function()

    with sqlite3.connect(db_dir / "optimization_metrics.db") as conn:
        cur = conn.execute("SELECT COUNT(*) FROM optimization_metrics")
        count = cur.fetchone()[0]
    assert count == 1
