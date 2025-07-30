import os
import sqlite3
from pathlib import Path

from template_engine.auto_generator import TemplateAutoGenerator
import template_engine.auto_generator as auto_generator


def create_test_dbs(tmp_path: Path):
    analytics_db = tmp_path / "analytics.db"
    completion_db = tmp_path / "template_completion.db"
    with sqlite3.connect(analytics_db) as conn:
        conn.execute("CREATE TABLE ml_pattern_optimization (id INTEGER PRIMARY KEY, replacement_template TEXT)")
        conn.executemany(
            "INSERT INTO ml_pattern_optimization (replacement_template) VALUES (?)",
            [("SELECT {cols} FROM {table}",), ("print('hello world')",)],
        )
    with sqlite3.connect(completion_db) as conn:
        conn.execute("CREATE TABLE templates (id INTEGER PRIMARY KEY, template_content TEXT)")
        conn.executemany(
            "INSERT INTO templates (template_content) VALUES (?)",
            [("def foo():\n    pass",), ("class Bar:\n    pass",)],
        )
    return analytics_db, completion_db


def test_auto_generator_cluster_representatives(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    analytics_db, completion_db = create_test_dbs(tmp_path)
    generator = TemplateAutoGenerator(analytics_db, completion_db)
    reps = generator.get_cluster_representatives()
    allowed = set(generator.templates + generator.patterns + generator._load_production_patterns())
    assert len(reps) == generator.cluster_model.n_clusters
    assert all(r in allowed for r in reps)


def test_pattern_templates_loaded(tmp_path: Path) -> None:
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    analytics_db, completion_db = create_test_dbs(tmp_path)
    generator = TemplateAutoGenerator(analytics_db, completion_db)
    assert any("DatabaseFirstOperator" in t for t in generator.templates)


def test_cluster_rep_no_dimension_error(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    analytics_db, completion_db = create_test_dbs(tmp_path)
    prod_db = tmp_path / "production.db"
    with sqlite3.connect(prod_db) as conn:
        conn.execute("CREATE TABLE script_template_patterns (template_content TEXT)")
        conn.execute("INSERT INTO script_template_patterns VALUES ('extra pattern')")
    gen = TemplateAutoGenerator(analytics_db, completion_db, production_db=prod_db)
    reps = gen.get_cluster_representatives()
    assert len(reps) == gen.cluster_model.n_clusters


def test_rank_templates_uses_similarity(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    analytics_db, completion_db = create_test_dbs(tmp_path)
    prod_db = tmp_path / "production.db"
    with sqlite3.connect(prod_db) as conn:
        conn.execute("CREATE TABLE code_templates (id INTEGER PRIMARY KEY, template_code TEXT)")
        conn.executemany(
            "INSERT INTO code_templates (template_code) VALUES (?)",
            [("foo",), ("bar",)],
        )
    gen = TemplateAutoGenerator(analytics_db, completion_db, production_db=prod_db)

    called = {"used": False}

    def fake_scores(*args, **kwargs):
        called["used"] = True
        return [(1, 0.1), (2, 0.9)]

    monkeypatch.setattr(auto_generator, "compute_similarity_scores", fake_scores)
    ranked = gen.rank_templates("bar")
    assert called["used"]
    assert ranked[0] == "bar"


def test_rank_templates_uses_quantum(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    analytics_db, completion_db = create_test_dbs(tmp_path)
    prod_db = tmp_path / "production.db"
    with sqlite3.connect(prod_db) as conn:
        conn.execute("CREATE TABLE code_templates (id INTEGER PRIMARY KEY, template_code TEXT)")
        conn.executemany(
            "INSERT INTO code_templates (template_code) VALUES (?)",
            [("foo",), ("bar",)],
        )
    gen = TemplateAutoGenerator(analytics_db, completion_db, production_db=prod_db)

    monkeypatch.setattr(auto_generator, "compute_similarity_scores", lambda *a, **k: [])

    def fake_qscore(text: str) -> float:
        return {"foo": 0.9, "bar": 0.1, "target": 0.85}.get(text, 0.0)

    monkeypatch.setattr(gen, "_quantum_score", fake_qscore)
    ranked = gen.rank_templates("target")
    assert ranked[0] == "foo"
