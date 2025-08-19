from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path

from scripts.compliance_score import fetch_score


def _create_db(path: Path, score: float) -> None:
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE compliance_metrics_history (ts INTEGER, composite_score REAL)"
    )
    conn.execute(
        "INSERT INTO compliance_metrics_history (ts, composite_score) VALUES (?, ?)",
        (1, score),
    )
    conn.commit()
    conn.close()


def test_fetch_score(tmp_path: Path) -> None:
    db = tmp_path / "analytics.db"
    _create_db(db, 88.5)
    assert fetch_score(db) == 88.5


def test_cli_output(tmp_path: Path) -> None:
    db = tmp_path / "analytics.db"
    _create_db(db, 55.5)
    result = subprocess.run(
        [sys.executable, "scripts/compliance_score.py", "--db", str(db)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(result.stdout) == {"score": 55.5}

