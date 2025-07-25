import sqlite3
from pathlib import Path

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


def test_auto_generator_cluster_representatives(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    analytics_db, completion_db = create_test_dbs(tmp_path)
    generator = TemplateAutoGenerator(analytics_db, completion_db)
    reps = generator.get_cluster_representatives()
    assert len(reps) == generator.cluster_model.n_clusters
    assert all(r in generator.templates or r in generator.patterns for r in reps)
