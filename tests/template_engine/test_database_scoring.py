import sqlite3
from pathlib import Path

import template_engine.auto_generator as auto_generator
from template_engine.auto_generator import TemplateAutoGenerator
from template_engine.db_first_code_generator import DBFirstCodeGenerator
import template_engine.db_first_code_generator as dbgen


def create_test_dbs(tmp_path: Path):
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    analytics_db = db_dir / "analytics.db"
    completion_db = db_dir / "template_completion.db"
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            "CREATE TABLE ml_pattern_optimization (id INTEGER PRIMARY KEY, replacement_template TEXT)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS generator_events ("
            "event TEXT, template_id INTEGER, score REAL, target TEXT,"
            "timestamp TEXT, module TEXT, level TEXT, duration REAL,"
            "count INTEGER, items INTEGER, clusters INTEGER, best_template TEXT"
            ")"
        )
        conn.execute(
            "INSERT INTO ml_pattern_optimization (replacement_template) VALUES (?)",
            ("print('db')",),
        )
    with sqlite3.connect(completion_db) as conn:
        conn.execute("CREATE TABLE templates (id INTEGER PRIMARY KEY, template_content TEXT)")
        conn.execute("INSERT INTO templates (template_content) VALUES ('fs_template')")
    return analytics_db, completion_db


def create_production_db(tmp_path: Path, text: str = "db_template") -> Path:
    db = tmp_path / "production.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE code_templates (id INTEGER PRIMARY KEY, template_code TEXT)")
        conn.execute("INSERT INTO code_templates (template_code) VALUES (?)", (text,))
        conn.execute("CREATE TABLE script_template_patterns (pattern_name TEXT PRIMARY KEY, template_content TEXT)")
        conn.execute(
            "INSERT INTO script_template_patterns (pattern_name, template_content) VALUES ('pat', ?)",
            (text,),
        )
    return db


def test_templates_loaded_from_database(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    analytics, completion = create_test_dbs(tmp_path)
    prod_db = create_production_db(tmp_path)
    gen = TemplateAutoGenerator(analytics, completion, production_db=prod_db)
    assert "db_template" in gen.templates


def test_similarity_scoring_hooks_used(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    analytics, completion = create_test_dbs(tmp_path)
    prod_db = create_production_db(tmp_path, "foo")
    gen = TemplateAutoGenerator(analytics, completion, production_db=prod_db)

    calls = {"scorer": False, "quant": False}

    def fake_scores(*args, **kwargs):
        calls["scorer"] = True
        return [(1, 0.9)]

    def fake_qsim(a: str, b: str) -> float:
        calls["quant"] = True
        return 0.9

    monkeypatch.setattr(auto_generator, "compute_similarity_scores", fake_scores)
    monkeypatch.setattr(gen, "_quantum_similarity", fake_qsim)
    ranked = gen.rank_templates("foo")
    assert ranked[0] == "foo"
    assert calls["scorer"] and calls["quant"]


def test_db_first_generation_output(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    prod = create_production_db(tmp_path, "print('hi')")
    dbgen.validate_enterprise_operation = lambda *a, **k: True
    gen = DBFirstCodeGenerator(prod, tmp_path / "doc.db", tmp_path / "tpl.db", tmp_path / "analytics.db")

    monkeypatch.setattr(auto_generator, "compute_similarity_scores", lambda *a, **k: [(1, 1.0)])
    monkeypatch.setattr(auto_generator, "quantum_similarity_score", lambda *a, **k: 1.0)

    result = gen.generate("print")
    assert "print('hi')" in result
