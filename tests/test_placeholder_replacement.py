import sqlite3
from pathlib import Path

from template_engine.placeholder_utils import find_placeholders, replace_placeholders


def test_find_placeholders():
    template = "Hello {{NAME}}, version {{VERSION}}"
    assert sorted(find_placeholders(template)) == ["NAME", "VERSION"]


def test_replace_placeholders(tmp_path: Path):
    prod = tmp_path / "production.db"
    tmpl_doc = tmp_path / "template_documentation.db"
    analytics = tmp_path / "analytics.db"
    with sqlite3.connect(prod) as conn:
        conn.execute(
            "CREATE TABLE template_placeholders (id INTEGER PRIMARY KEY, placeholder_name TEXT, default_value TEXT)"
        )
        conn.executemany(
            "INSERT INTO template_placeholders (placeholder_name, default_value) VALUES (?, ?)",
            [("{{NAME}}", "World"), ("{{VERSION}}", "1.0")],
        )
    # ensure template_doc exists
    sqlite3.connect(tmpl_doc).close()

    result = replace_placeholders(
        "Hello {{NAME}}, version {{VERSION}}!",
        {"production": prod, "template_doc": tmpl_doc, "analytics": analytics},
    )
    assert result == "Hello World, version 1.0!"
    with sqlite3.connect(analytics) as conn:
        count = conn.execute("SELECT COUNT(*) FROM placeholder_replacements").fetchone()[0]
    assert count == 2
