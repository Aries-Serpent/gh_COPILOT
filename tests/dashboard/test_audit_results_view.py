import sqlite3
from pathlib import Path

import pytest

from dashboard import enterprise_dashboard as ed


@pytest.fixture()
def app(tmp_path: Path, monkeypatch):
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE todo_fixme_tracking (placeholder_type TEXT, status TEXT)"
        )
        conn.execute(
            "INSERT INTO todo_fixme_tracking VALUES ('TODO', 'open')"
        )
    monkeypatch.setattr(ed, "ANALYTICS_DB", db)
    return ed.app


def test_audit_results_json(app):
    client = app.test_client()
    data = client.get("/audit-results").get_json()
    assert data == [{"placeholder_type": "TODO", "count": 1}]


def test_audit_results_view(app):
    client = app.test_client()
    resp = client.get("/audit-results/view")
    assert resp.status_code == 200
