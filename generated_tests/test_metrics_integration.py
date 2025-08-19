# generated_tests/test_metrics_integration.py
# Integration tests with temporary SQLite DBs using pytest's tmp_path fixture.
# https://docs.pytest.org/en/stable/how-to/tmp_path.html

import sqlite3
import json
from pathlib import Path
import importlib.util
import sys


def _load_workflow(root: Path):
    wf = root / "codex_workflow.py"
    spec = importlib.util.spec_from_file_location("codex_workflow", wf)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["codex_workflow"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_temp_sqlite_pipeline(tmp_path: Path):
    mon = tmp_path / "monitoring.db"
    conn = sqlite3.connect(str(mon))
    conn.execute(
        "CREATE TABLE system_metrics (cpu_pct REAL, mem_pct REAL, errors_per_min REAL);",
    )
    conn.execute(
        "INSERT INTO system_metrics (cpu_pct, mem_pct, errors_per_min) VALUES (42.0, 55.5, 1.0);",
    )
    conn.commit()
    conn.close()

    root = Path.cwd()
    workflow = _load_workflow(root)

    workflow.DB_MON = mon
    workflow.DB_ANAL = tmp_path / "analytics.db"

    metrics = workflow.collect_all_metrics()
    assert metrics.get("cpu_pct") == 42.0
    assert metrics.get("errors_per_min") == 1.0

    msg = workflow.emergency_guard(metrics, {"cpu_pct": 40.0, "error_rate": 5.0})
    assert isinstance(msg, str) and "exceeds threshold" in msg
