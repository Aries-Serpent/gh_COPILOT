"""Tests for unified_monitoring_optimization_system utilities."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
import pytest

from quantum_algorithm_library_expansion import quantum_score_stub

from unified_monitoring_optimization_system import (
    detect_anomalies,
    push_metrics,
    auto_heal_session,
    record_quantum_score,
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


def test_detect_anomalies_flags_and_persists_outlier(tmp_path: Path) -> None:
    """Anomalies should include scores and be stored in ``analytics.db``."""

    history = [
        {"cpu": 10.0, "mem": 20.0},
        {"cpu": 12.0, "mem": 22.0},
        {"cpu": 95.0, "mem": 99.0},
    ]

    db = tmp_path / "analytics.db"
    anomalies = detect_anomalies(history, contamination=0.34, db_path=db)

    assert len(anomalies) == 1
    anomaly = anomalies[0]
    assert "anomaly_score" in anomaly
    assert "composite_score" in anomaly
    if quantum_score_stub is not None:
        expected = (
            anomaly["anomaly_score"] + quantum_score_stub(history[-1].values())
        ) / 2
        assert anomaly["composite_score"] == pytest.approx(expected)

    with sqlite3.connect(db) as conn:
        row = conn.execute(
            "SELECT metrics_json, anomaly_score, quantum_score, composite_score FROM anomaly_results"
        ).fetchone()

    assert row is not None
    assert json.loads(row[0]) == {"cpu": 95.0, "mem": 99.0}
    assert row[1] == anomaly["anomaly_score"]
    assert row[3] == anomaly["composite_score"]
    if quantum_score_stub is not None:
        assert row[2] == pytest.approx(quantum_score_stub(history[-1].values()))


def test_auto_heal_session_restarts_on_anomaly(tmp_path: Path) -> None:
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
    db = tmp_path / "analytics.db"
    anomalies = detect_anomalies(history, contamination=0.34, db_path=db)
    restarted = auto_heal_session(
        anomalies=anomalies, manager=mgr, db_path=db
    )

    assert restarted is True
    assert mgr.started == 1
    assert mgr.ended == 1


def test_record_quantum_score_persists_value(tmp_path: Path) -> None:
    """Quantum scores should be stored for later analysis."""

    metrics = {"cpu": 1.0, "mem": 2.0}
    db = tmp_path / "analytics.db"
    score = record_quantum_score(metrics, db_path=db)

    with sqlite3.connect(db) as conn:
        row = conn.execute(
            "SELECT metrics_json, score FROM quantum_scores"
        ).fetchone()

    assert row is not None
    assert json.loads(row[0]) == metrics
    assert row[1] == pytest.approx(score)


def test_auto_heal_session_ignores_normal_metrics(tmp_path: Path) -> None:
    """No restart should occur when metrics are within normal ranges."""

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
        {"cpu": 5.0, "mem": 10.0},
        {"cpu": 5.0, "mem": 10.0},
    ]

    mgr = DummyManager()
    db = tmp_path / "analytics.db"
    restarted = auto_heal_session(
        history, contamination=0.01, manager=mgr, db_path=db
    )

    assert restarted is False
    assert mgr.started == 0
    assert mgr.ended == 0
