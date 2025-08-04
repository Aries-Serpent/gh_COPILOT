"""Tests for unified_monitoring_optimization_system utilities."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from unified_monitoring_optimization_system import (
    detect_anomalies,
    record_quantum_score,
    push_metrics,
    auto_heal_session,
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


def test_auto_heal_session_restarts_on_anomaly() -> None:
    """Anomalies should trigger a restart via the session manager."""

    class DummyManager:
        def __init__(self) -> None:
            self.started = 0
            self.ended = 0

        def start_session(self) -> None:  # pragma: no cover - simple increment
            self.started += 1

        def end_session(self) -> None:  # pragma: no cover - simple increment
            self.ended += 1

    history = [
        {"cpu": 5.0, "mem": 10.0},
        {"cpu": 6.0, "mem": 11.0},
        {"cpu": 95.0, "mem": 99.0},
    ]

    mgr = DummyManager()
    restarted = auto_heal_session(history, contamination=0.34, manager=mgr)

    assert restarted is True
    assert mgr.started == 1
    assert mgr.ended == 1
