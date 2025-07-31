import sqlite3
from pathlib import Path

from docs.quantum_template_generator import generate_default_templates


def create_production_db(tmp_path: Path) -> Path:
    db = tmp_path / "production.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE templates (id INTEGER PRIMARY KEY, template_content TEXT)")
        conn.executemany(
            "INSERT INTO templates (template_content) VALUES (?)",
            [("def foo(): pass",), ("class Bar: pass",)],
        )
        conn.execute("CREATE TABLE ml_pattern_optimization (id INTEGER PRIMARY KEY, replacement_template TEXT)")
        conn.execute("INSERT INTO ml_pattern_optimization (replacement_template) VALUES ('print(\"hi\")')")
    return db


def test_generate_default_templates(tmp_path):
    db = create_production_db(tmp_path)
    results = generate_default_templates(db)
    assert results
    assert all(isinstance(t[0], str) and isinstance(t[1], float) for t in results)
