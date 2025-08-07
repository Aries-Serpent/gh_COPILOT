from __future__ import annotations

import sqlite3
from pathlib import Path

from web_gui.scripts.flask_apps.database_web_connector import DatabaseWebConnector


def test_fetch_dashboard_alerts_handles_missing_table(tmp_path: Path) -> None:
    db = tmp_path / "test.db"
    sqlite3.connect(db).close()
    connector = DatabaseWebConnector(db)
    assert connector.fetch_dashboard_alerts() == []
    assert connector.fetch_zero_byte_logs() == []


def test_fetch_dashboard_alerts_returns_data(tmp_path: Path) -> None:
    db = tmp_path / "test.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE dashboard_alerts (alert_type TEXT, alert_message TEXT, created_at TEXT)"
        )
        conn.execute(
            "INSERT INTO dashboard_alerts VALUES ('info','hello','2024-01-01')"
        )
        conn.execute(
            "CREATE TABLE zero_byte_logs (file_path TEXT, detected_at TEXT)"
        )
        conn.execute(
            "INSERT INTO zero_byte_logs VALUES ('/tmp/a','2024-01-02')"
        )
        conn.commit()
    connector = DatabaseWebConnector(db)
    alerts = connector.fetch_dashboard_alerts()
    zero_logs = connector.fetch_zero_byte_logs()
    assert alerts[0]["alert_type"] == "info"
    assert zero_logs[0]["file_path"] == "/tmp/a"
