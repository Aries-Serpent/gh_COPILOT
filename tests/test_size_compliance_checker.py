import sqlite3
from pathlib import Path

from scripts.database import size_compliance_checker as checker


def test_check_database_sizes_pass(tmp_path: Path) -> None:
    db = tmp_path / "ok.db"
    sqlite3.connect(db).close()
    assert checker.check_database_sizes(tmp_path, threshold_mb=1)


def test_check_database_sizes_failure(tmp_path: Path) -> None:
    big = tmp_path / "big.db"
    with sqlite3.connect(big) as conn:
        conn.execute("CREATE TABLE data(x TEXT)")
        payload = "x" * 1024
        for _ in range(1200):
            conn.execute("INSERT INTO data(x) VALUES (?)", (payload,))
        conn.commit()
    assert not checker.check_database_sizes(tmp_path, threshold_mb=1)
