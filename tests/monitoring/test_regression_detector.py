import sqlite3
from pathlib import Path

from scripts.monitoring import regression_detector as rd


def test_detect_regressions_and_db(tmp_path: Path) -> None:
    metrics = tmp_path / "m.txt"
    metrics.write_text("10\n10\n10\n30\n")
    db = tmp_path / "analytics.db"
    code = rd.main([
        "--metric-file",
        str(metrics),
        "--db-path",
        str(db),
        "--window",
        "3",
        "--threshold",
        "5",
    ])
    assert code == 1
    with sqlite3.connect(db) as conn:
        rows = conn.execute("SELECT value, sma FROM regressions").fetchall()
    assert rows and rows[0][0] == 30.0

