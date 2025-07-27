import sqlite3
from pathlib import Path
from typing import Any

import scripts.automation.system_maintenance_scheduler as sms


class DummyMonitor:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def _get_system_metrics(self) -> dict[str, Any]:
        return {"uptime_seconds": 1}

    def _write_metrics(self, metrics: dict[str, Any]) -> None:
        pass


def test_run_cycle(tmp_path: Path, monkeypatch) -> None:
    workspace = tmp_path
    (workspace / "databases").mkdir()
    analytics_db = workspace / "analytics.db"
    production_db = workspace / "databases" / "production.db"
    with sqlite3.connect(production_db) as conn:
        conn.execute(
            (
                "CREATE TABLE IF NOT EXISTS unified_wrapup_sessions ("
                "session_id TEXT PRIMARY KEY, start_time TEXT, end_time TEXT, "
                "status TEXT, compliance_score REAL, error_details TEXT)"
            )
        )
        conn.commit()

    monkeypatch.setattr(sms, "_run_self_healing", lambda w: None)
    monkeypatch.setattr(sms, "ContinuousOperationMonitor", lambda *a, **k: DummyMonitor())

    sms.maintenance_cycle(workspace)

    with sqlite3.connect(analytics_db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM system_maintenance_jobs").fetchone()[0]
    assert count == 1

    with sqlite3.connect(production_db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM unified_wrapup_sessions").fetchone()[0]
    assert count == 1
