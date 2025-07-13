import sqlite3
from pathlib import Path

from database_consolidation_migration import consolidate_databases



def benchmark_queries():
    """Benchmark database queries"""
    return []

def _make_db(path: Path, table: str) -> Path:
    with sqlite3.connect(path) as conn:
        conn.execute(f"CREATE TABLE {table} (id INTEGER)")
        conn.execute(f"INSERT INTO {table} (id) VALUES (1)")
    return path


def test_consolidate_databases(tmp_path):
    src1 = _make_db(tmp_path / "a.db", "t1")
    src2 = _make_db(tmp_path / "b.db", "t2")
    target = tmp_path / "analytics.db"
    _make_db(target, "t0")
    consolidate_databases(target, [src1, src2])
    with sqlite3.connect(target) as conn:
        assert conn.execute("SELECT COUNT(*) FROM t1").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM t2").fetchone()[0] == 1
    metrics = benchmark_queries(["SELECT COUNT(*) FROM t1"], db_path=target)
    assert metrics["within_time_target"]
