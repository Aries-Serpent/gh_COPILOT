"""Integration tests for performance validation framework."""

import sqlite3

from performance_validation_framework import PerformanceValidationFramework


def test_store_baseline(tmp_path) -> None:
    """Baseline metrics should persist to the provided database."""
    db_file = tmp_path / "perf.db"
    framework = PerformanceValidationFramework(db_path=str(db_file))
    framework.store_baseline({"metric": 1.0})

    with sqlite3.connect(db_file) as conn:
        value = conn.execute(
            "SELECT value FROM performance_baseline WHERE metric='metric'"
        ).fetchone()[0]
    assert value == 1.0

