"""Tests for analytics logging helpers via the helper CLI."""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path


def test_cli_logs_into_temp_analytics_db(tmp_path: Path) -> None:
    """The helper CLI should write rows to events and sync_events_log tables."""

    har_data = {
        "log": {
            "entries": [
                {
                    "request": {"method": "GET", "url": "https://example.com"},
                    "time": 42,
                }
            ]
        }
    }

    har_path = tmp_path / "sample.har"
    har_path.write_text(json.dumps(har_data), encoding="utf-8")

    db_path = tmp_path / "analytics.db"

    env = os.environ.copy()
    env["TEST_MODE"] = "1"
    env["ANALYTICS_DB_PATH"] = str(db_path)

    cmd = [sys.executable, "-m", "tools.har_cli", str(har_path)]
    subprocess.run(cmd, check=True, env=env, cwd=str(Path(__file__).resolve().parents[1]))

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM events")
    assert cur.fetchone()[0] == 2  # started and completed

    cur.execute("SELECT file_path, count, status FROM sync_events_log")
    row = cur.fetchone()
    assert row is not None
    assert row[0].endswith("sample.har")
    assert row[1] == 1
    assert row[2] == "SUCCESS"

    conn.close()

