import sqlite3
from pathlib import Path

import pytest

from dashboard import enterprise_dashboard as ed


@pytest.fixture()
def app_with_placeholder_audit(tmp_path: Path, monkeypatch):
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE placeholder_audit (placeholder_type TEXT)")
        conn.execute("INSERT INTO placeholder_audit VALUES ('TODO')")
    monkeypatch.setattr(ed, "ANALYTICS_DB", db)
    return ed.app


@pytest.fixture()
def app_with_todo_table(tmp_path: Path, monkeypatch):
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE todo_fixme_tracking (placeholder_type TEXT, status TEXT)"
        )
        conn.execute("INSERT INTO todo_fixme_tracking VALUES ('TODO', 'open')")
    monkeypatch.setattr(ed, "ANALYTICS_DB", db)
    return ed.app


def test_audit_results_json(app_with_placeholder_audit):
    client = app_with_placeholder_audit.test_client()
    data = client.get("/audit-results").get_json()
    assert data == [{"placeholder_type": "TODO", "count": 1}]


def test_audit_results_json_fallback(app_with_todo_table):
    client = app_with_todo_table.test_client()
    data = client.get("/audit-results").get_json()
    assert data == [{"placeholder_type": "TODO", "count": 1}]


def test_audit_results_view(app_with_placeholder_audit):
    client = app_with_placeholder_audit.test_client()
    resp = client.get("/audit-results/view")
    assert resp.status_code == 200
