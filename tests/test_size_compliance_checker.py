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
    with sqlite3.connect(db2) as conn:
        conn.execute("CREATE TABLE data(x TEXT)")
        payload = "y" * 1024
        for _ in range(1200):
            conn.execute("INSERT INTO data(x) VALUES (?)", (payload,))
        conn.commit()
    results = checker.check_database_sizes(tmp_path, threshold_mb=1)
    assert results["big.db"] > 1
    violations = list(stream_events("size_violations", db_path=db_file))
    assert violations


def test_table_size_violation(tmp_path: Path, capsys) -> None:
    db_file = tmp_path / "analytics.db"
    os.environ["ANALYTICS_DB"] = str(db_file)
    checker.ANALYTICS_DB = db_file

    target = tmp_path / "oversize.db"
    with sqlite3.connect(target) as conn:
        conn.execute("CREATE TABLE big(data TEXT)")
        payload = "x" * 1024
        for _ in range(2000):
            conn.execute("INSERT INTO big(data) VALUES (?)", (payload,))
        conn.commit()

    checker.check_database_sizes(tmp_path, threshold_mb=0.5)
    output = capsys.readouterr().out
    violations = list(stream_events("size_violations", db_path=db_file))
    assert any("\"table_name\": \"big\"" in v for v in violations)
    assert "data:" in output
