import shutil
import sqlite3
from pathlib import Path

from monitoring.performance_tracker import record_error, track_query_time


def _prepare_db(tmp_path: Path) -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    db_path = tmp_path / "analytics.db"
    shutil.copy(repo_root / "analytics.db", db_path)
    return db_path


def test_track_query_time_records_and_computes(tmp_path, monkeypatch):
    db = _prepare_db(tmp_path)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    metrics = track_query_time("q1", 40.0, db_path=db)
    assert metrics["avg_response_time_ms"] == 40.0
    assert metrics["error_rate"] == 0.0


def test_record_error_updates_error_rate(tmp_path, monkeypatch):
    db = _prepare_db(tmp_path)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    track_query_time("q1", 40.0, db_path=db)
    metrics = record_error("q1", db_path=db)
    assert metrics["error_rate"] == 0.5
