"""Tests for unified_monitoring_optimization_system utilities."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from unified_monitoring_optimization_system import (
    detect_anomalies,
    push_metrics,
)


def test_push_metrics_links_session(tmp_path: Path) -> None:
    """Metrics should be associated with a session ID when provided."""

    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE unified_wrapup_sessions (session_id TEXT PRIMARY KEY)"
        )
        conn.execute(
            "INSERT INTO unified_wrapup_sessions (session_id) VALUES ('abc')"
        )

    push_metrics({"cpu": 1.0}, session_id="abc", db_path=db)

    with sqlite3.connect(db) as conn:
        row = conn.execute(
            "SELECT session_id, metrics_json FROM monitoring_metrics"
        ).fetchone()

    assert row == ("abc", json.dumps({"cpu": 1.0}))


def test_detect_anomalies_flags_outlier() -> None:
    """An obvious outlier should be returned by the detector."""

    history = [
        {"cpu": 10.0, "mem": 20.0},
        {"cpu": 12.0, "mem": 22.0},
        {"cpu": 95.0, "mem": 99.0},
    ]

    anomalies = detect_anomalies(history, contamination=0.34)
    assert history[-1] in anomalies
    assert len(anomalies) == 1

