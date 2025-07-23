"""Test unified logging helper."""

import sqlite3
from pathlib import Path

from template_engine.log_utils import _log_event


def test_log_event_tables(tmp_path: Path) -> None:
    db = tmp_path / "analytics.db"
    tables = ["sync_events_log", "sync_status", "doc_analysis"]
    for table in tables:
        _log_event({"t": table}, table=table, db_path=db)
        with sqlite3.connect(db) as conn:
            rows = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        assert rows == 1

