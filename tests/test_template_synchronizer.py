# [Test]: Template Synchronizer Integration & Compliance
# > Generated: 2025-07-21 20:36:06 | Author: mbaetion

import sqlite3
from pathlib import Path

from template_engine import template_synchronizer


def create_db(path: Path, templates: dict[str, str]) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            "CREATE TABLE templates (name TEXT PRIMARY KEY, template_content TEXT)"
        )
        conn.executemany(
            "INSERT INTO templates (name, template_content) VALUES (?, ?)",
            list(templates.items()),
        )

def test_synchronize_templates(tmp_path: Path, monkeypatch) -> None:
    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"
    analytics = tmp_path / "analytics.db"
    create_db(db_a, {"t1": "foo"})
    create_db(db_b, {"t2": "bar"})
    monkeypatch.setattr(template_synchronizer, "ANALYTICS_DB", analytics)
    template_synchronizer.synchronize_templates([db_a, db_b])

    for db in [db_a, db_b]:
        with sqlite3.connect(db) as conn:
            rows = conn.execute(
                "SELECT name, template_content FROM templates ORDER BY name"
            ).fetchall()
            assert rows == [("t1", "foo"), ("t2", "bar")]
    with sqlite3.connect(analytics) as conn:
        count = conn.execute("SELECT COUNT(*) FROM sync_events").fetchone()[0]
        assert count == 2

def test_invalid_templates_ignored(tmp_path: Path, monkeypatch) -> None:
    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"
    analytics = tmp_path / "analytics.db"
    create_db(db_a, {"t1": "foo", "empty": ""})
    create_db(db_b, {})
    monkeypatch.setattr(template_synchronizer, "ANALYTICS_DB", analytics)
    template_synchronizer.synchronize_templates([db_a, db_b])

    with sqlite3.connect(db_b) as conn:
        rows = conn.execute("SELECT name FROM templates ORDER BY name").fetchall()
        assert rows == [("t1",)]

    with sqlite3.connect(analytics) as conn:
        count = conn.execute("SELECT COUNT(*) FROM sync_events").fetchone()[0]
        assert count == 2

def test_audit_logging_and_rollback(tmp_path: Path, monkeypatch) -> None:
    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"
    create_db(db_a, {"good": "foo"})
    # create db_b without templates table to force failure
    with sqlite3.connect(db_b) as conn:
        conn.execute("CREATE TABLE other(id INTEGER)")
    analytics = tmp_path / "analytics.db"
    monkeypatch.setattr(template_synchronizer, "ANALYTICS_DB", analytics)
    template_synchronizer.synchronize_templates([db_a, db_b])

    # db_b should remain unchanged because sync rolled back
    with sqlite3.connect(db_b) as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        assert tables == [("other",)]

    with sqlite3.connect(analytics) as conn:
        audit_count = conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
        event_count = conn.execute("SELECT COUNT(*) FROM sync_events").fetchone()[0]
        assert audit_count == 1
        assert event_count == 1