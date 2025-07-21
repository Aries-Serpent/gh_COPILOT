import sqlite3
from pathlib import Path

from template_engine.template_synchronizer import synchronize_templates


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
    create_db(db_a, {"t1": "foo"})
    create_db(db_b, {"t2": "bar"})
    monkeypatch.chdir(tmp_path)
    synchronize_templates([db_a, db_b])
    for db in [db_a, db_b]:
        with sqlite3.connect(db) as conn:
            rows = conn.execute("SELECT name, template_content FROM templates ORDER BY name").fetchall()
            assert rows == [("t1", "foo"), ("t2", "bar")]

    with sqlite3.connect(tmp_path / "analytics.db") as conn:
        rows = conn.execute("SELECT name, source FROM templates_sync_log ORDER BY name, source").fetchall()
        assert rows == [
            ("t1", str(db_a)),
            ("t1", str(db_b)),
            ("t2", str(db_a)),
            ("t2", str(db_b)),
        ]


def test_invalid_templates_ignored(tmp_path: Path, monkeypatch) -> None:
    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"
    create_db(db_a, {"t1": "foo", "empty": ""})
    create_db(db_b, {})

    monkeypatch.chdir(tmp_path)
    synchronize_templates([db_a, db_b])

    with sqlite3.connect(db_b) as conn:
        rows = conn.execute("SELECT name FROM templates ORDER BY name").fetchall()
        assert rows == [("t1",),]
