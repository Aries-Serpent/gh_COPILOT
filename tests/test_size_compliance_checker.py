import os
import sqlite3
from pathlib import Path

from scripts.database import size_compliance_checker as checker
from utils.log_utils import stream_events


def test_check_database_sizes(tmp_path: Path) -> None:
    db_file = tmp_path / "analytics.db"
    os.environ["ANALYTICS_DB"] = str(db_file)
    checker.ANALYTICS_DB = db_file
    db1 = tmp_path / "small.db"
    sqlite3.connect(db1).close()
    results = checker.check_database_sizes(tmp_path, threshold_mb=1)
    assert results["small.db"] <= 1

    db2 = tmp_path / "big.db"
    db2.write_bytes(b"0" * (2 * 1024 * 1024))  # 2 MB
    results = checker.check_database_sizes(tmp_path, threshold_mb=1)
    assert results["big.db"] > 1
    violations = list(stream_events("size_violations", db_path=db_file))
    assert violations
