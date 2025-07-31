import sqlite3
import asyncio
from pathlib import Path

from scripts.optimization.windows_compatible_optimizer import WindowsCompatibleOptimizer
from scripts.optimization.windows_compatible_optimizer_async import (
    WindowsCompatibleOptimizer as WindowsCompatibleOptimizerAsync,
)


def _create_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "sample.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE t(id INTEGER PRIMARY KEY, value TEXT)")
        conn.executemany("INSERT INTO t(value) VALUES (?)", [("a",), ("b",)])
    return db_path


def test_analyze_database_health(tmp_path):
    db_path = _create_db(tmp_path)
    opt = WindowsCompatibleOptimizer()
    opt.workspace_path = tmp_path
    opt.results_dir = tmp_path / "results"
    opt.results_dir.mkdir(parents=True, exist_ok=True)
    health = opt.analyze_database_health("sample", str(db_path))
    assert health.table_count == 1
    assert health.record_count == 2
    assert health.health_score > 0


def test_async_analyze_database_health(tmp_path):
    db_path = _create_db(tmp_path)
    opt = WindowsCompatibleOptimizerAsync()
    opt.workspace_path = tmp_path
    health = asyncio.run(opt._analyze_database_health(db_path))
    assert health is not None
    assert health.table_count == 1
    assert health.record_count == 2
