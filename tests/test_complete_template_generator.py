#!/usr/bin/env python3
import sqlite3
from pathlib import Path

<<<<<<< HEAD
from scripts.utilities.complete_template_generator import CompleteTemplateGenerator
=======
from complete_template_generator import CompleteTemplateGenerator
import logging
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)


def create_dbs(tmp_path: Path):
    analytics = tmp_path / "analytics.db"
    completion = tmp_path / "template_completion.db"
    production = tmp_path / "production.db"
    with sqlite3.connect(analytics) as conn:
        conn.execute(
            "CREATE TABLE ml_pattern_optimization (id INTEGER PRIMARY KEY, \
                replacement_template TEXT)"
        )
        conn.executemany(
            "INSERT INTO ml_pattern_optimization (replacement_template) VALUES (?)",
            [("print('a')",), ("print('b')",)],
        )
    with sqlite3.connect(completion) as conn:
<<<<<<< HEAD
        conn.execute("CREATE TABLE templates (id INTEGER PRIMARY KEY, template_content TEXT)")
        conn.execute("INSERT INTO templates (template_content) VALUES ('def foo():\n    pass')")
=======
        conn.execute(
            "CREATE TABLE templates (id INTEGER PRIMARY KEY, template_content TEXT)"
        )
        conn.execute(
            "INSERT INTO templates (template_content) VALUES ('def foo():\n    pass')"
        )
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
    # create empty production.db
    sqlite3.connect(production).close()
    return analytics, completion, production


def test_create_templates(tmp_path):
    analytics, completion, production = create_dbs(tmp_path)
    gen = CompleteTemplateGenerator(analytics, completion, production)
    templates = gen.create_templates()
    assert templates
    with sqlite3.connect(production) as conn:
<<<<<<< HEAD
        count = conn.execute("SELECT COUNT(*) FROM template_generation_stats").fetchone()[0]
    assert count == len(templates)
    recorded = conn.execute("SELECT COUNT(*) FROM generated_templates").fetchone()[0]
    assert recorded == len(templates)
=======
        count = conn.execute(
            "SELECT COUNT(*) FROM template_generation_stats"
        ).fetchone()[0]
    assert count == len(templates)
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)


def test_regenerate_templates(tmp_path):
    analytics, completion, production = create_dbs(tmp_path)
    gen = CompleteTemplateGenerator(analytics, completion, production)
    templates1 = gen.create_templates()
    templates2 = gen.regenerate_templates()
    assert templates1 == templates2
<<<<<<< HEAD


def test_create_templates_handles_extra_templates(tmp_path):
    analytics, completion, production = create_dbs(tmp_path)
    # Insert an additional completion template to ensure templates outnumber
    # analytics patterns, reproducing the previously failing scenario.
    with sqlite3.connect(completion) as conn:
        conn.execute(
            "INSERT INTO templates (template_content) VALUES ('def bar():\n    return 42')"
        )
    gen = CompleteTemplateGenerator(analytics, completion, production)
    templates = gen.create_templates()
    assert len(templates) >= 2
=======
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
