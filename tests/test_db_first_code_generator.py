import os
import sqlite3
from pathlib import Path

os.environ.setdefault("GH_COPILOT_DISABLE_VALIDATION", "1")

from template_engine import db_first_code_generator
from template_engine.db_first_code_generator import DBFirstCodeGenerator


def create_production_db(tmp_path: Path) -> Path:
    db = tmp_path / "production.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            """CREATE TABLE script_template_patterns (
                pattern_name TEXT PRIMARY KEY,
                pattern_type TEXT,
                template_content TEXT,
                variables_json TEXT,
                usage_count INTEGER,
                created_timestamp TEXT,
                last_used_timestamp TEXT
            )"""
        )
        conn.execute(
            "INSERT INTO script_template_patterns (pattern_name, pattern_type, template_content) VALUES (?, ?, ?)",
            ("Objective1", "script", "print('hi')"),
        )
        conn.commit()
    return db


def test_existing_pattern_loaded(tmp_path: Path) -> None:
    prod_db = create_production_db(tmp_path)
    db_first_code_generator.validate_enterprise_operation = lambda *args, **kwargs: True
    gen = DBFirstCodeGenerator(
        prod_db,
        tmp_path / "documentation.db",
        tmp_path / "template_documentation.db",
        tmp_path / "analytics.db",
    )
    result = gen.generate("Objective1")
    assert "print('hi')" in result


def test_missing_pattern_triggers_database_lookup(tmp_path: Path, monkeypatch) -> None:
    prod_db = create_production_db(tmp_path)
    db_first_code_generator.validate_enterprise_operation = lambda *args, **kwargs: True
    gen = DBFirstCodeGenerator(
        prod_db,
        tmp_path / "documentation.db",
        tmp_path / "template_documentation.db",
        tmp_path / "analytics.db",
    )
    called = {"count": 0}

    def fake_fetch(name: str) -> None:
        called["count"] += 1
        return None

    monkeypatch.setattr(gen, "fetch_existing_pattern", fake_fetch)
    gen.generate("missing_template")
    assert called["count"] > 0
