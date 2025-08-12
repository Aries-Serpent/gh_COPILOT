"""Tests for service health monitoring."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from ghc_monitoring.service_health import check_service
from web_gui.monitoring.alerting import notification_engine


def test_check_service_alerts(monkeypatch, tmp_path: Path) -> None:
    """Ensure a down service records uptime and triggers alerts."""

    notification_engine.NOTIFICATION_LOG.clear()
    notification_engine.EMAIL_LOG.clear()
    notification_engine.SMS_LOG.clear()

    def fake_get(url: str, timeout: int = 5):  # pragma: no cover - simple stub
        raise OSError("connection refused")

    monkeypatch.setattr("ghc_monitoring.service_health.requests.get", fake_get)
    db = tmp_path / "health.db"
    result = check_service("sync", "http://localhost:1/health", db_path=db)
    assert result is False
    with sqlite3.connect(db) as conn:
        row = conn.execute(
            "SELECT service, status FROM service_uptime"
        ).fetchone()
    assert row == ("sync", "down")
    assert any("sync service unreachable" in msg for msg in notification_engine.NOTIFICATION_LOG)
    assert notification_engine.EMAIL_LOG
    assert notification_engine.SMS_LOG
