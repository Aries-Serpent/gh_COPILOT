import os
import sqlite3
from pathlib import Path

from template_engine.auto_generator import TemplateAutoGenerator
import template_engine.auto_generator as auto_generator
from utils.lessons_learned_integrator import ensure_lessons_table

os.environ.setdefault("GH_COPILOT_DISABLE_VALIDATION", "1")


def create_test_dbs(tmp_path: Path):
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    analytics_db = db_dir / "analytics.db"
    completion_db = db_dir / "template_completion.db"
    with sqlite3.connect(analytics_db) as conn:
        conn.execute("CREATE TABLE ml_pattern_optimization (id INTEGER PRIMARY KEY, replacement_template TEXT)")
        conn.execute(
            "CREATE TABLE IF NOT EXISTS generator_events (event TEXT, template_id INTEGER, score REAL, target TEXT)"
        )
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


def test_cluster_deterministic(tmp_path: Path, monkeypatch) -> None:
    """Repeated initialisation should yield stable clustering."""
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    analytics_db, completion_db = create_test_dbs(tmp_path)
    gen1 = TemplateAutoGenerator(analytics_db, completion_db)
    gen2 = TemplateAutoGenerator(analytics_db, completion_db)
    assert gen1.get_cluster_representatives() == gen2.get_cluster_representatives()


def test_pattern_templates_loaded(tmp_path: Path) -> None:
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    analytics_db, completion_db = create_test_dbs(tmp_path)
    generator = TemplateAutoGenerator(analytics_db, completion_db)
    assert any("DatabaseFirstOperator" in t for t in generator.templates)


def test_lesson_templates_ranked(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    analytics_db, completion_db = create_test_dbs(tmp_path)
    gen = TemplateAutoGenerator(analytics_db, completion_db)
    monkeypatch.setattr(auto_generator, "compute_similarity_scores", lambda *a, **k: [])
    monkeypatch.setattr(auto_generator, "quantum_similarity_score", lambda *a, **k: 0.0)
    monkeypatch.setattr(auto_generator, "quantum_cluster_score", lambda *a, **k: 0.0)
    monkeypatch.setattr(gen, "_quantum_similarity", lambda *a, **k: 0.0)
    monkeypatch.setattr(gen, "_quantum_score", lambda *a, **k: 0.0)
    ranked = gen.rank_templates("DatabaseFirstOperator")
    assert any("DatabaseFirstOperator" in t for t in ranked)


def test_lessons_dataset_integrated(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    analytics_db, completion_db = create_test_dbs(tmp_path)
    monkeypatch.setattr(
        auto_generator,
        "load_lessons",
        lambda: [{"description": "Lesson template"}],
    )
    monkeypatch.setattr(auto_generator, "apply_lessons", lambda *a, **k: None)
    gen = TemplateAutoGenerator(analytics_db, completion_db)
    assert any("Lesson template" in t for t in gen.templates)


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

    calls = []

    def wrapped(text: str) -> float:
        calls.append(text)
        return fake_qscore(text)

    monkeypatch.setattr(gen, "_quantum_score", wrapped)
    gen.templates = ["foo", "bar"]
    gen.patterns = []
    monkeypatch.setattr(gen, "_quantum_similarity", lambda *a: 0.0)
    monkeypatch.setattr(auto_generator, "quantum_similarity_score", lambda *a: 0.0)
    monkeypatch.setattr(auto_generator, "quantum_cluster_score", lambda *a: 0.0)

    ranked = gen.rank_templates("target")
    assert "target" in calls and "foo" in calls and "bar" in calls
    assert ranked[0] == "foo"


def test_quantum_text_score_influences_ranking(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    analytics_db = tmp_path / "databases" / "analytics.db"
    completion_db = tmp_path / "template_completion.db"
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute("CREATE TABLE ml_pattern_optimization (id INTEGER PRIMARY KEY, replacement_template TEXT)")
        conn.execute(
            "CREATE TABLE IF NOT EXISTS generator_events (event TEXT, template_id INTEGER, score REAL, target TEXT)"
        )
        conn.execute("INSERT INTO ml_pattern_optimization (replacement_template) VALUES ('foo')")
    with sqlite3.connect(completion_db) as conn:
        conn.execute("CREATE TABLE templates (id INTEGER PRIMARY KEY, template_content TEXT)")
        conn.executemany(
            "INSERT INTO templates (template_content) VALUES (?)",
            [("foo",), ("bar",)],
        )
    gen = TemplateAutoGenerator(analytics_db, completion_db)
    gen.templates = ["foo", "bar"]
    gen.patterns = []

    monkeypatch.setattr(auto_generator, "compute_similarity_scores", lambda *a, **k: [])
    monkeypatch.setattr(auto_generator, "quantum_similarity_score", lambda *a: 0.0)
    monkeypatch.setattr(auto_generator, "quantum_cluster_score", lambda *a: 0.0)
    monkeypatch.setattr(gen, "_quantum_similarity", lambda *a: 0.0)

    scores = {"foo": 0.95, "bar": 0.2, "target": 0.9}
    monkeypatch.setattr(gen, "_quantum_score", lambda text: scores.get(text, 0.0))

    ranked = gen.rank_templates("target")
    assert ranked[0] == "foo"


def test_rank_templates_combines_quantum_scores(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_TEST_MODE", "1")
    analytics_db = tmp_path / "databases" / "analytics.db"
    completion_db = tmp_path / "template_completion.db"
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute("CREATE TABLE ml_pattern_optimization (id INTEGER PRIMARY KEY, replacement_template TEXT)")
    with sqlite3.connect(completion_db) as conn:
        conn.execute("CREATE TABLE templates (id INTEGER PRIMARY KEY, template_content TEXT)")
        conn.executemany(
            "INSERT INTO templates (template_content) VALUES (?)",
            [("foo",), ("bar",)],
        )
    events: list[dict] = []
    monkeypatch.setattr(auto_generator, "_log_event", lambda e, **k: events.append(e))
    gen = TemplateAutoGenerator(analytics_db, completion_db)
    gen.templates = ["foo", "bar"]
    gen.patterns = []

    monkeypatch.setattr(auto_generator, "compute_similarity_scores", lambda *a, **k: [])
    monkeypatch.setattr(gen, "_quantum_similarity", lambda *a, **k: 0.5)
    monkeypatch.setattr(auto_generator, "quantum_similarity_score", lambda *a, **k: 0.5)
    monkeypatch.setattr(auto_generator, "quantum_cluster_score", lambda *a, **k: 0.5)

    scores = {"foo": 0.9, "bar": 0.2, "target": 0.8}
    monkeypatch.setattr(gen, "_quantum_score", lambda text: scores.get(text, 0.0))

    ranked = gen.rank_templates("target")
    assert ranked[0] == "foo"
    assert any(ev.get("event") == "quantum_total" for ev in events)


def test_quantum_import_failure(monkeypatch):
    """AutoGenerator handles missing quantum library gracefully."""
    import importlib
    import builtins
    import numpy as np

    orig_import_module = importlib.import_module
    orig_import = builtins.__import__

    def fake_import_module(name, package=None):
        if name == "quantum_algorithm_library_expansion":
            raise ImportError("missing")
        return orig_import_module(name, package)

    def fake_builtin(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "quantum_algorithm_library_expansion":
            raise ImportError("missing")
        return orig_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(importlib, "import_module", fake_import_module)
    monkeypatch.setattr(builtins, "__import__", fake_builtin)
    import sys

    sys.modules.pop("template_engine.auto_generator", None)
    auto_gen = importlib.import_module("template_engine.auto_generator")

    assert auto_gen.quantum_text_score("hi") == 0.0
    assert auto_gen.quantum_similarity_score([1.0], [1.0]) == 0.0
    assert auto_gen.quantum_cluster_score(np.array([[1.0]])) == 0.0


def test_lessons_applied_during_generation(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    analytics_db, completion_db = create_test_dbs(tmp_path)
    learning_db = tmp_path / "learning_monitor.db"
    ensure_lessons_table(learning_db)
    with sqlite3.connect(learning_db) as conn:
        conn.execute(
            "INSERT INTO enhanced_lessons_learned VALUES (?,?,?,?,?)",
            (
                "integrate tests",
                "unit",
                "2024-01-01T00:00:00Z",
                "validated",
                "testing",
            ),
        )
    original_load = auto_generator.load_lessons
    monkeypatch.setattr(
        auto_generator, "load_lessons", lambda: original_load(db_path=learning_db)
    )
    applied = {"called": False}

    original_apply = auto_generator.apply_lessons

    def tracking_apply(logger, lessons):
        applied["called"] = True
        original_apply(logger, lessons)

    monkeypatch.setattr(auto_generator, "apply_lessons", tracking_apply)

    gen = TemplateAutoGenerator(analytics_db, completion_db)
    gen.generate_template({"action": "print"})

    assert applied["called"]
    assert any("integrate tests" in t for t in gen.templates)


def test_validate_no_recursive_folders_ignores_venv(tmp_path: Path, monkeypatch) -> None:
    """Virtual environments may contain backup-like paths that should be ignored."""
    (tmp_path / ".venv/lib/python/backupsearch").mkdir(parents=True)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    auto_generator.validate_no_recursive_folders()  # Should not raise
