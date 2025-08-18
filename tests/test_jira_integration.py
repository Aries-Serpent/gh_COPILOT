"""Tests for Jira integration."""

from __future__ import annotations

import sqlite3
from unittest.mock import Mock

import requests

from scripts.integration.jira_integration import jira_create_ticket


def test_feature_flag_disables(monkeypatch, tmp_path) -> None:
    """Creation is skipped when feature flag is disabled."""

    db_path = tmp_path / "analytics.db"
    session = Mock()

    monkeypatch.setenv("JIRA_INTEGRATION_ENABLED", "0")

    result = jira_create_ticket("id1", {"summary": "s"}, session=session, db_path=db_path)
    assert result is None
    assert not session.post.called
    assert not db_path.exists()


def test_api_error_handling(monkeypatch, tmp_path) -> None:
    """Errors from the API are logged to the database."""

    db_path = tmp_path / "analytics.db"
    session = Mock()
    response = Mock()
    response.raise_for_status.side_effect = requests.HTTPError("boom")
    session.post.return_value = response

    monkeypatch.setenv("JIRA_INTEGRATION_ENABLED", "1")
    monkeypatch.setenv("JIRA_API_TOKEN", "t")
    monkeypatch.setenv("JIRA_API_URL", "https://example.atlassian.net")

    result = jira_create_ticket("id2", {"summary": "s"}, session=session, db_path=db_path)
    assert result is None

    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT status, details FROM integration_events ORDER BY id",
    ).fetchall()
    conn.close()

    assert rows == [("failure", "boom")]

