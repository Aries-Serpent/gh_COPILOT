import sqlite3
from pathlib import Path

from scripts.database.size_compliance_checker import check_database_sizes


def test_check_database_sizes(tmp_path: Path) -> None:
    db1 = tmp_path / "small.db"
    sqlite3.connect(db1).close()
    assert check_database_sizes(tmp_path, threshold_mb=1)

    db2 = tmp_path / "big.db"
    db2.write_bytes(b"0" * (2 * 1024 * 1024))  # 2 MB
    assert not check_database_sizes(tmp_path, threshold_mb=1)
