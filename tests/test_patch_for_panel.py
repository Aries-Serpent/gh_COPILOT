import os
import sqlite3
import tempfile
from pathlib import Path


def _make_temp_db(schema_sql: str, rows_sql: list[str]):
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(schema_sql)
        for sql in rows_sql:
            conn.execute(sql)
        conn.commit()
    finally:
        conn.close()
    return Path(db_path)


def test_panel_changes_when_db_changes(monkeypatch):
    schema = """
    CREATE TABLE IF NOT EXISTS code_quality_metrics(
        id INTEGER PRIMARY KEY,
        ts TEXT,
        score REAL,
        lint REAL,
        tests REAL,
        placeholders REAL
    );
    """
    rowA = (
        "INSERT INTO code_quality_metrics(ts,score,lint,tests,placeholders)"
        " VALUES('2025-01-01T00:00:00Z',70,80,60,75);"
    )
    rowB = (
        "INSERT INTO code_quality_metrics(ts,score,lint,tests,placeholders)"
        " VALUES('2025-01-02T00:00:00Z',77,82,70,78);"
    )

    temp_db = _make_temp_db(schema, [rowA])
    monkeypatch.setenv("TEST_MODE", "1")
    monkeypatch.setenv("ANALYTICS_DB_PATH", str(temp_db))

    from src.analytics.metrics_reader import get_latest_panel_snapshot

    first = get_latest_panel_snapshot("compliance", temp_db, test_mode=True)
    assert first["ok"] and first["snapshot"]["score"] == 70

    conn = sqlite3.connect(temp_db.as_posix())
    try:
        conn.execute(rowB)
        conn.commit()
    finally:
        conn.close()

    second = get_latest_panel_snapshot("compliance", temp_db, test_mode=True)
    assert second["ok"] and second["snapshot"]["score"] == 77
    assert second["ts"] == "2025-01-02T00:00:00Z"
