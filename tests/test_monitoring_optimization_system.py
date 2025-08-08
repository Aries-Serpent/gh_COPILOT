#!/usr/bin/env python3
<<<<<<< HEAD
import sqlite3
from pathlib import Path

from scripts.monitoring.unified_monitoring_optimization_system import EnterpriseUtility


def create_dbs(workspace: Path) -> None:
    db_dir = workspace / "databases"
    db_dir.mkdir()
    perf_db = db_dir / "performance_monitoring.db"
    with sqlite3.connect(perf_db) as conn:
        conn.execute(
            (
                "CREATE TABLE performance_metrics ("
                "cpu_percent REAL, memory_percent REAL, "
                "disk_usage_percent REAL, network_io_bytes REAL)"
            )
        )
        conn.execute("INSERT INTO performance_metrics VALUES (10, 10, 10, 10)")
    opt_db = db_dir / "optimization_metrics.db"
    with sqlite3.connect(opt_db) as conn:
        conn.execute(
            (
                "CREATE TABLE optimization_metrics ("
                "session_id TEXT, timestamp TEXT, performance_delta REAL, "
                "cpu_usage REAL, memory_usage REAL, disk_io REAL, "
                "metrics_json TEXT)"
            )
        )


def test_perform_utility_function_inserts_metrics(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    create_dbs(tmp_path)
    util = EnterpriseUtility(workspace_path=str(tmp_path))
    assert util.perform_utility_function()

    with sqlite3.connect(tmp_path / "databases" / "optimization_metrics.db") as conn:
        count = conn.execute("SELECT COUNT(*) FROM optimization_metrics").fetchone()[0]
    assert count == 1


def test_default_workspace_uses_env(tmp_path, monkeypatch):
    """Ensure EnterpriseUtility defaults to the workspace environment variable."""
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    util = EnterpriseUtility()
    assert util.workspace_path == Path(tmp_path)
=======
import shutil
import sqlite3
from pathlib import Path

from unified_monitoring_optimization_system import EnterpriseUtility
import logging


def test_perform_utility_function_inserts_metrics(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[1]
    workspace = tmp_path
    db_dir = workspace / "databases"
    db_dir.mkdir()
    shutil.copy(repo_root / "databases" / "performance_monitoring.db", db_dir)
    shutil.copy(repo_root / "databases" / "optimization_metrics.db", db_dir)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))

    util = EnterpriseUtility(workspace_path=str(workspace))
    assert util.perform_utility_function()

    with sqlite3.connect(db_dir / "optimization_metrics.db") as conn:
        cur = conn.execute("SELECT COUNT(*) FROM optimization_metrics")
        count = cur.fetchone()[0]
    assert count == 1
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
