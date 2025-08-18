"""Tests for SAP integration sync."""

from __future__ import annotations

import sqlite3
from unittest.mock import Mock

from scripts.integration.sap_integration import sap_sync


def test_feature_flag_disables(monkeypatch, tmp_path) -> None:
    """Sync is skipped when feature flag is not enabled."""

    db_path = tmp_path / "analytics.db"
    session = Mock()

    monkeypatch.setenv("SAP_INTEGRATION_ENABLED", "0")

    result = sap_sync("id1", session=session, db_path=db_path)
    assert result is None
    assert not session.get.called
    assert not db_path.exists()


def test_idempotent_sync(monkeypatch, tmp_path) -> None:
    """Repeated sync calls with same id only hit API once and log events."""

    db_path = tmp_path / "analytics.db"
    session = Mock()
    response = Mock()
    response.json.return_value = {"detail": "ok"}
    response.raise_for_status.return_value = None
    session.get.return_value = response

    monkeypatch.setenv("SAP_INTEGRATION_ENABLED", "1")
    monkeypatch.setenv("SAP_API_KEY", "k")
    monkeypatch.setenv("SAP_API_URL", "https://example.com")

    sap_sync("abc", session=session, db_path=db_path)
    sap_sync("abc", session=session, db_path=db_path)

    assert session.get.call_count == 1

    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT status FROM integration_events ORDER BY id"
    ).fetchall()
    conn.close()

    assert rows == [("success",), ("skipped",)]

