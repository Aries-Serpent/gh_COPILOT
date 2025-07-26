# [Test]: Template Synchronizer Integration & Compliance
# > Generated: 2025-07-21 20:36:06 | Author: mbaetion

import os
import sqlite3
from pathlib import Path

from template_engine import template_synchronizer


def create_db(path: Path, templates: dict[str, str]) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE templates (name TEXT PRIMARY KEY, template_content TEXT)")
        conn.executemany(
            "INSERT INTO templates (name, template_content) VALUES (?, ?)",
            list(templates.items()),
        )


def test_synchronize_templates(tmp_path: Path, monkeypatch) -> None:
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"
    analytics = tmp_path / "analytics.db"
    create_db(db_a, {"t1": "foo"})
    create_db(db_b, {"t2": "bar"})
    monkeypatch.setattr(template_synchronizer, "ANALYTICS_DB", analytics)
    template_synchronizer.synchronize_templates_real([db_a, db_b])

    with sqlite3.connect(db_a) as conn:
        rows = conn.execute("SELECT name, template_content FROM templates ORDER BY name").fetchall()
        assert rows == [("t1", "foo")]
    with sqlite3.connect(db_b) as conn:
        rows = conn.execute("SELECT name, template_content FROM templates ORDER BY name").fetchall()
        assert rows == [("t2", "bar")]
    assert not analytics.exists()

def test_invalid_templates_ignored(tmp_path: Path, monkeypatch) -> None:
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"
    analytics = tmp_path / "analytics.db"
    create_db(db_a, {"t1": "foo", "empty": ""})
    create_db(db_b, {})
    monkeypatch.setattr(template_synchronizer, "ANALYTICS_DB", analytics)
    template_synchronizer.synchronize_templates_real([db_a, db_b])

    with sqlite3.connect(db_b) as conn:
        rows = conn.execute("SELECT name FROM templates ORDER BY name").fetchall()
        assert rows == []

    assert not analytics.exists()

def test_audit_logging_and_rollback(tmp_path: Path, monkeypatch) -> None:
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"
    create_db(db_a, {"good": "foo"})
    # create db_b without templates table to force failure
    with sqlite3.connect(db_b) as conn:
        conn.execute("CREATE TABLE other(id INTEGER)")
    analytics = tmp_path / "analytics.db"
    monkeypatch.setattr(template_synchronizer, "ANALYTICS_DB", analytics)
    template_synchronizer.synchronize_templates_real([db_a, db_b])

    # db_b should remain unchanged because sync rolled back
    with sqlite3.connect(db_b) as conn:
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        assert tables == [("other",)]

    assert not analytics.exists()


def test_extract_templates(tmp_path: Path) -> None:
    db = tmp_path / "temp.db"
    create_db(db, {"n1": "c1"})
    results = template_synchronizer._extract_templates(db)
    assert results == [("n1", "c1")]


def test_can_write_analytics(tmp_path: Path, monkeypatch) -> None:
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    outside = tmp_path.parent / "analytics.db"
    monkeypatch.setattr(template_synchronizer, "ANALYTICS_DB", outside)
    assert template_synchronizer._can_write_analytics()

    inside = tmp_path / "analytics.db"
    monkeypatch.setattr(template_synchronizer, "ANALYTICS_DB", inside)
    assert not template_synchronizer._can_write_analytics()
