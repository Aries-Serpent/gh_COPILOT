#!/usr/bin/env python3
import sqlite3
from pathlib import Path

import numpy as np
import pytest
from template_engine.auto_generator import TemplateAutoGenerator


def create_test_dbs(tmp_path: Path):
    analytics_db = tmp_path / "analytics.db"
    completion_db = tmp_path / "template_completion.db"
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            "CREATE TABLE ml_pattern_optimization (id INTEGER PRIMARY KEY, \
                replacement_template TEXT)"
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
            "CREATE TABLE ml_pattern_optimization (id INTEGER PRIMARY KEY, \
                replacement_template TEXT)"
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


def test_get_cluster_representatives(tmp_path):
    analytics_db, completion_db = create_test_dbs(tmp_path)
    generator = TemplateAutoGenerator(analytics_db, completion_db)
    reps = generator.get_cluster_representatives()
    assert len(reps) == generator.cluster_model.n_clusters
    assert all(r in generator.templates or r in generator.patterns for r in reps)


def test_objective_similarity(tmp_path):
    analytics_db, completion_db = create_test_dbs(tmp_path)
    generator = TemplateAutoGenerator(analytics_db, completion_db)
    template = generator.templates[0]
    score = generator.objective_similarity(template, template)
    assert score > 0.9


def test_select_best_template(tmp_path):
    analytics_db, completion_db = create_test_dbs(tmp_path)
    generator = TemplateAutoGenerator(analytics_db, completion_db)
    target = generator.templates[0]
    best = generator.select_best_template(target)
    assert best == target


def test_quantum_score(tmp_path):
    analytics_db, completion_db = create_test_dbs(tmp_path)
    generator = TemplateAutoGenerator(analytics_db, completion_db)
    score = generator._quantum_score("dummy")
    assert 0.0 <= score <= 1.0


def test_refresh_templates_updates_cluster(tmp_path):
    analytics_db, completion_db = create_test_dbs(tmp_path)
    generator = TemplateAutoGenerator(analytics_db, completion_db)
    initial_centers = generator.cluster_model.cluster_centers_.copy()
    generator._refresh_templates()
    assert not np.array_equal(initial_centers, generator.cluster_model.cluster_centers_)
