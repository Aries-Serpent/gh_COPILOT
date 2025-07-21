#!/usr/bin/env python3
import sqlite3
from pathlib import Path

from scripts.automation.template_auto_generation_complete import TemplateSynthesisEngine


def create_dbs(tmp_path: Path):
    analytics = tmp_path / "analytics.db"
    completion = tmp_path / "template_completion.db"
    with sqlite3.connect(analytics) as conn:
        conn.execute(
            "CREATE TABLE ml_pattern_optimization (id INTEGER PRIMARY KEY, \
                replacement_template TEXT)"
        )
        conn.executemany(
            "INSERT INTO ml_pattern_optimization (replacement_template) VALUES (?)",
            [("print('x')",), ("print('y')",)],
        )
    with sqlite3.connect(completion) as conn:
        conn.execute(
            "CREATE TABLE templates (id INTEGER PRIMARY KEY, template_content TEXT)"
        )
        conn.execute(
            "INSERT INTO templates (template_content) VALUES ('def foo():\n    pass')"
        )
    return analytics, completion


def test_synthesize_templates(tmp_path):
    analytics, completion = create_dbs(tmp_path)
    engine = TemplateSynthesisEngine(analytics, completion)
    templates = engine.synthesize_templates()
    assert templates
