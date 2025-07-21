# [Test]: Template Synchronizer Integration Test
# > Generated: 2025-07-21 20:23:01 | Author: mbaetiong

import sqlite3
import importlib.util
from pathlib import Path

# Dynamically load the synchronizer for testing
spec = importlib.util.spec_from_file_location(
    "template_synchronizer",
    Path(__file__).resolve().parents[1] / "template_engine" / "template_synchronizer.py",
)
template_synchronizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(template_synchronizer)
synchronize_templates = template_synchronizer.synchronize_templates

def create_db(path: Path, templates: dict[str, str]) -> None:
    """Create a SQLite DB and insert provided templates."""
    with sqlite3.connect(path) as conn:
        conn.execute(
            "CREATE TABLE templates (name TEXT PRIMARY KEY, template_content TEXT)"
        )
        conn.executemany(
            "INSERT INTO templates (name, template_content) VALUES (?, ?)",
            list(templates.items()),
        )

def test_synchronize_templates(tmp_path: Path) -> None:
    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"
    analytics_db = tmp_path / "analytics.db"
    create_db(db_a, {"t1": "foo"})
    create_db(db_b, {"t2": "bar"})
    synchronize_templates([db_a, db_b], analytics_db=analytics_db)
    # Both DBs should now contain both templates
    for db in [db_a, db_b]:
        with sqlite3.connect(db) as conn:
            rows = conn.execute("SELECT name, template_content FROM templates ORDER BY name").fetchall()
            assert rows == [("t1", "foo"), ("t2", "bar")]
    # Analytics log should capture successful sync
    with sqlite3.connect(analytics_db) as conn:
        result = conn.execute("SELECT result FROM template_sync_log ORDER BY timestamp DESC LIMIT 1").fetchone()[0]
        assert result == "success"
        count = conn.execute("SELECT COUNT(*) FROM templates_sync_log").fetchone()[0]
        assert count == 2

def test_invalid_templates_rollback(tmp_path: Path) -> None:
    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"
    analytics_db = tmp_path / "analytics.db"
    create_db(db_a, {"t1": "foo", "empty": ""})
    create_db(db_b, {})
    synchronize_templates([db_a, db_b], analytics_db=analytics_db)
    # Only valid templates should be synced
    with sqlite3.connect(db_b) as conn:
        rows = conn.execute("SELECT name FROM templates ORDER BY name").fetchall()
        assert rows == [("t1",),]
    # Analytics log should capture only successful syncs
    with sqlite3.connect(analytics_db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM templates_sync_log").fetchone()[0]
        assert count == 1

def test_templates_logged(tmp_path: Path) -> None:
    db_a = tmp_path / "a.db"
    analytics_db = tmp_path / "analytics.db"
    create_db(db_a, {"t1": "foo"})
    synchronize_templates([db_a], analytics_db=analytics_db)
    # Log must reflect templates and source DBs
    with sqlite3.connect(analytics_db) as conn:
        rows = conn.execute(
            "SELECT template_name, source_db FROM templates_sync_log"
        ).fetchall()
    assert rows == [("t1", str(db_a))]