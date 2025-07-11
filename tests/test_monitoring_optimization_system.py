import shutil
import sqlite3
from pathlib import Path

from unified_monitoring_optimization_system import EnterpriseUtility


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
