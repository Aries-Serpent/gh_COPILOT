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


def test_synchronize_templates(tmp_path: Path) -> None:
    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"
    create_db(db_a, {"t1": "foo"})
    create_db(db_b, {"t2": "bar"})
    synchronize_templates([db_a, db_b])
    for db in [db_a, db_b]:
        with sqlite3.connect(db) as conn:
            rows = conn.execute("SELECT name, template_content FROM templates ORDER BY name").fetchall()
            assert rows == [("t1", "foo"), ("t2", "bar")]
