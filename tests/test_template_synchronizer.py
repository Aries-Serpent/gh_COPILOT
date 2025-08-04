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


def test_can_write_analytics(tmp_path: Path, monkeypatch) -> None:
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    analytics = tmp_path.parent / "analytics.db"
    monkeypatch.setattr(template_synchronizer, "ANALYTICS_DB", analytics)
    assert template_synchronizer._can_write_analytics() is True

    monkeypatch.setattr(template_synchronizer, "ANALYTICS_DB", tmp_path / "analytics.db")
    assert template_synchronizer._can_write_analytics() is False


def test_extract_templates(tmp_path: Path) -> None:
    db = tmp_path / "test.db"
    assert template_synchronizer._extract_templates(db) == []
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE templates (name TEXT PRIMARY KEY, template_content TEXT)")
        conn.execute("INSERT INTO templates VALUES ('a', 'b')")
    assert template_synchronizer._extract_templates(db) == [("a", "b")]


def test_synchronize_with_clustering(tmp_path: Path, monkeypatch) -> None:
    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"
    analytics = tmp_path / "analytics.db"
    create_db(db_a, {"t1": "foo bar"})
    create_db(db_b, {"t2": "bar baz"})
    monkeypatch.setattr(template_synchronizer, "ANALYTICS_DB", analytics)

    called: dict[str, bool] = {"flag": False}

    def dummy_cluster(templates: dict[str, str]) -> dict[str, str]:
        called["flag"] = True
        return templates

    monkeypatch.setattr(template_synchronizer, "_cluster_templates", dummy_cluster)

    synced = template_synchronizer.synchronize_templates_real([db_a, db_b], cluster=True)
    assert synced == 2
    with sqlite3.connect(analytics) as conn:
        count = conn.execute("SELECT COUNT(*) FROM sync_events_log").fetchone()[0]
        assert count >= 3
    assert called["flag"] is True


def test_simulation_with_clustering(tmp_path: Path, monkeypatch) -> None:
    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"
    analytics = tmp_path / "analytics.db"
    create_db(db_a, {"t1": "foo bar"})
    create_db(db_b, {"t2": "bar baz"})
    monkeypatch.setattr(template_synchronizer, "ANALYTICS_DB", analytics)

    called: dict[str, bool] = {"flag": False}

    def dummy_cluster(templates: dict[str, str]) -> dict[str, str]:
        called["flag"] = True
        return templates

    monkeypatch.setattr(template_synchronizer, "_cluster_templates", dummy_cluster)

    synced = template_synchronizer.synchronize_templates([db_a, db_b], cluster=True)
    assert synced == 2
    assert called["flag"] is True


def test_cluster_templates_logs_metrics(tmp_path: Path, monkeypatch) -> None:
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    analytics = tmp_path.parent / "analytics.db"
    monkeypatch.setattr(template_synchronizer, "ANALYTICS_DB", analytics)
    templates = {"t1": "foo bar", "t2": "bar baz", "t3": "baz qux"}
    reps = template_synchronizer._cluster_templates(templates, n_clusters=2)
    assert reps
    with sqlite3.connect(analytics) as conn:
        row = conn.execute(
            "SELECT inertia, silhouette, n_clusters FROM template_sync_cluster_metrics"
        ).fetchone()
    assert row is not None
    inertia, silhouette, n_clusters = row
    assert inertia >= 0
    assert -1.0 <= silhouette <= 1.0
    assert n_clusters == 2
