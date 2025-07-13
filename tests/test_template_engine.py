import sqlite3
from pathlib import Path

import pytest

from template_engine.auto_generator import TemplateAutoGenerator


def create_test_dbs(tmp_path: Path):
    analytics_db = tmp_path / "analytics.db"
    completion_db = tmp_path / "template_completion.db"
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            "CREATE TABLE ml_pattern_optimization (id INTEGER PRIMARY KEY, replacement_template TEXT)"
        )
        conn.executemany(
            "INSERT INTO ml_pattern_optimization (replacement_template) VALUES (?)",
            [("SELECT {cols} FROM {table}",), ("print('hello world')",)],
        )
    with sqlite3.connect(completion_db) as conn:
        conn.execute(
            "CREATE TABLE templates (id INTEGER PRIMARY KEY, template_content TEXT)"
        )
        conn.executemany(
            "INSERT INTO templates (template_content) VALUES (?)",
            [("def foo():\n    pass",), ("class Bar:\n    pass",)],
        )
    return analytics_db, completion_db


def test_generate_template_returns_expected(tmp_path):
    analytics_db, completion_db = create_test_dbs(tmp_path)
    generator = TemplateAutoGenerator(analytics_db, completion_db)
    template = generator.generate_template({"action": "print"})
    assert "print" in template


def test_generate_template_no_patterns(tmp_path):
    generator = TemplateAutoGenerator(tmp_path / "a.db", tmp_path / "c.db")
    assert generator.generate_template({"any": "thing"}) == ""


def test_template_regeneration(tmp_path):
    analytics_db, completion_db = create_test_dbs(tmp_path)
    generator = TemplateAutoGenerator(analytics_db, completion_db)
    template = generator.generate_template({"action": "print"})
    assert generator.regenerate_template() == template


def test_generate_template_invalid_syntax(tmp_path):
    analytics_db = tmp_path / "analytics.db"
    completion_db = tmp_path / "template_completion.db"
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            "CREATE TABLE ml_pattern_optimization (id INTEGER PRIMARY KEY, replacement_template TEXT)"
        )
        conn.execute(
            "INSERT INTO ml_pattern_optimization (replacement_template) VALUES ('def invalid:')"
        )
    with sqlite3.connect(completion_db) as conn:
        conn.execute(
            "CREATE TABLE templates (id INTEGER PRIMARY KEY, template_content TEXT)"
        )
    generator = TemplateAutoGenerator(analytics_db, completion_db)
    with pytest.raises(ValueError):
        generator.generate_template({"action": "invalid"})
