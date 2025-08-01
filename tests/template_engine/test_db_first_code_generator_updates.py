"""Tests for updated DB-first code generator features."""

import os
import sqlite3
from pathlib import Path

os.environ.setdefault("GH_COPILOT_DISABLE_VALIDATION", "1")

from template_engine.db_first_code_generator import TemplateAutoGenerator
from template_engine import db_first_code_generator


def test_load_templates_prefers_database(tmp_path: Path) -> None:
    completion_db = tmp_path / "templates.db"
    production_db = tmp_path / "production.db"
    analytics_db = tmp_path / "analytics.db"

    with sqlite3.connect(completion_db) as conn:
        conn.execute("CREATE TABLE templates (template_content TEXT)")
        conn.execute("INSERT INTO templates (template_content) VALUES ('db_template')")

    with sqlite3.connect(production_db) as conn:
        conn.execute("CREATE TABLE code_templates (id INTEGER PRIMARY KEY, template_code TEXT)")
        conn.execute("INSERT INTO code_templates (template_code) VALUES ('prod_template')")

    gen = TemplateAutoGenerator(
        analytics_db=analytics_db,
        completion_db=completion_db,
        production_db=production_db,
    )
    assert gen.templates == ["db_template"]


def test_cluster_patterns_logs_quantum_score(tmp_path: Path, monkeypatch) -> None:
    analytics_db = tmp_path / "analytics.db"
    gen = TemplateAutoGenerator(
        analytics_db=analytics_db,
        completion_db=tmp_path / "templates.db",
        production_db=tmp_path / "production.db",
    )
    gen.templates = ["alpha", "beta"]
    calls = []
    monkeypatch.setattr(
        db_first_code_generator,
        "quantum_cluster_score",
        lambda m: calls.append(m) or 0.5,
    )
    events: list[dict] = []
    monkeypatch.setattr(db_first_code_generator, "_log_event", lambda data, **_: events.append(data))
    gen._cluster_patterns()
    assert calls
    assert any(e.get("event") == "quantum_cluster_score" for e in events)


def test_rank_templates_logs_duration(tmp_path: Path, monkeypatch) -> None:
    prod_db = tmp_path / "production.db"
    with sqlite3.connect(prod_db) as conn:
        conn.execute("CREATE TABLE code_templates (id INTEGER PRIMARY KEY, template_code TEXT)")
        conn.execute("INSERT INTO code_templates (template_code) VALUES ('foo')")
        conn.execute("INSERT INTO code_templates (template_code) VALUES ('bar')")

    gen = TemplateAutoGenerator(
        analytics_db=tmp_path / "analytics.db",
        completion_db=tmp_path / "templates.db",
        production_db=prod_db,
    )

    monkeypatch.setattr(
        db_first_code_generator,
        "compute_similarity_scores",
        lambda *_, **__: [(1, 0.1), (2, 0.2)],
    )
    events: list[dict] = []
    monkeypatch.setattr(db_first_code_generator, "_log_event", lambda data, **_: events.append(data))
    gen.rank_templates("foo")
    assert any(e.get("event") == "rank_duration" for e in events)

