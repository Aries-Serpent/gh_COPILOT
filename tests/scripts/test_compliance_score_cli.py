from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from subprocess import check_output


REPO_ROOT = Path(__file__).resolve().parents[2]


def _run_cli(*args: str) -> dict[str, float]:
    cmd = ["python", "-m", "scripts.compliance_score_cli", *args]
    output = check_output(cmd, cwd=REPO_ROOT)
    return json.loads(output.decode("utf-8"))


def test_reports_score_when_db_present(tmp_path: Path) -> None:
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE compliance_metrics_history (ts INTEGER, composite_score REAL)"
        )
        conn.execute(
            "INSERT INTO compliance_metrics_history (ts, composite_score) VALUES (1, 7.5)"
        )
        conn.commit()

    result = _run_cli("--db", str(db))
    assert result["score"] == 7.5


def test_defaults_to_zero_when_db_missing(tmp_path: Path) -> None:
    missing = tmp_path / "missing.db"
    result = _run_cli("--db", str(missing))
    assert result["score"] == 0.0

