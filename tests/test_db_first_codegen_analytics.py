import os
import sqlite3
from pathlib import Path

from template_engine.db_first_code_generator import DBFirstCodeGenerator
from template_engine import auto_generator
import template_engine.db_first_code_generator as dbgen

auto_generator.validate_no_recursive_folders = lambda: None
dbgen.validate_enterprise_operation = lambda *a, **k: None


def test_auto_generation_logs_event(tmp_path: Path) -> None:
    prod_db = tmp_path / "production.db"
    doc_db = tmp_path / "documentation.db"
    tpl_db = tmp_path / "template.db"
    analytics = tmp_path / "analytics.db"

    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"
    gen = DBFirstCodeGenerator(prod_db, doc_db, tpl_db, analytics)
    result = gen.generate("TestObjective")
    assert "Auto-generated template" in result

    with sqlite3.connect(analytics) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM code_generation_events WHERE objective = ?",
            ("TestObjective",),
        ).fetchone()[0]
    assert count == 1


def test_generate_integration_ready_code(tmp_path: Path) -> None:
    prod_db = tmp_path / "production.db"
    doc_db = tmp_path / "documentation.db"
    tpl_db = tmp_path / "template.db"
    analytics = tmp_path / "analytics.db"

    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"
    gen = DBFirstCodeGenerator(prod_db, doc_db, tpl_db, analytics)
    path = gen.generate_integration_ready_code("Obj")
    assert path.exists()
    with sqlite3.connect(analytics) as conn:
        count = conn.execute("SELECT COUNT(*) FROM code_generation_events WHERE status='integration-ready'").fetchone()[
            0
        ]
    assert count == 1
