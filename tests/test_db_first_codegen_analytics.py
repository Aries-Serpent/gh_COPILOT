import os
import sqlite3
from pathlib import Path
import pytest

from template_engine.db_first_code_generator import DBFirstCodeGenerator
from template_engine import auto_generator
import template_engine.db_first_code_generator as dbgen

auto_generator.validate_no_recursive_folders = lambda: None
dbgen.validate_enterprise_operation = lambda *a, **k: None


def test_auto_generation_logs_event(tmp_path: Path) -> None:
    prod_db = tmp_path / "production.db"
    doc_db = tmp_path / "documentation.db"
    tpl_db = tmp_path / "template.db"
    analytics = tmp_path / "databases" / "analytics.db"
    analytics.parent.mkdir()

    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"
    dbgen._log_event = lambda *a, **k: None
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
    analytics = tmp_path / "databases" / "analytics.db"
    analytics.parent.mkdir()

    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"
    with sqlite3.connect(prod_db) as conn:
        conn.execute(
            "CREATE TABLE template_placeholders (placeholder_name TEXT, default_value TEXT)"
        )
        conn.execute(
            "INSERT INTO template_placeholders VALUES ('{{NAME}}', 'World')"
        )

    def fake_log(event: dict, *, table: str, db_path: Path, **_: object) -> None:
        with sqlite3.connect(db_path) as conn:
            conn.execute(f"CREATE TABLE IF NOT EXISTS {table} (event TEXT)")
            conn.execute(
                f"INSERT INTO {table} (event) VALUES (?)",
                (event.get("event"),),
            )
            conn.commit()

    dbgen._log_event = fake_log

    gen = DBFirstCodeGenerator(prod_db, doc_db, tpl_db, analytics)
    gen.select_best_template = lambda *_: "print('{{NAME}}')"
    path = gen.generate_integration_ready_code("Obj")
    assert path.exists()
    assert path.read_text() == "print('World')"
    with sqlite3.connect(analytics) as conn:
        gen_count = conn.execute(
            "SELECT COUNT(*) FROM generator_events WHERE event='integration_ready_generated'"
        ).fetchone()[0]
        corr_count = conn.execute(
            "SELECT COUNT(*) FROM correction_logs WHERE event='code_generated'"
        ).fetchone()[0]
    assert gen_count == 1 and corr_count == 1


def test_integration_ready_updates_tracking(tmp_path: Path) -> None:
    prod_db = tmp_path / "production.db"
    doc_db = tmp_path / "documentation.db"
    tpl_db = tmp_path / "template.db"
    analytics = tmp_path / "databases" / "analytics.db"
    analytics.parent.mkdir()

    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"
    with sqlite3.connect(prod_db) as conn:
        conn.execute(
            "CREATE TABLE template_placeholders (placeholder_name TEXT, default_value TEXT)"
        )
        conn.execute("INSERT INTO template_placeholders VALUES ('{{NAME}}', 'World')")

    def fake_log(event: dict, *, table: str, db_path: Path, **_: object) -> None:
        with sqlite3.connect(db_path) as conn:
            conn.execute(f"CREATE TABLE IF NOT EXISTS {table} (event TEXT)")
            conn.execute(f"INSERT INTO {table} (event) VALUES (?)", (event.get("event"),))
            conn.commit()

    dbgen._log_event = fake_log

    gen = DBFirstCodeGenerator(prod_db, doc_db, tpl_db, analytics)
    gen.select_best_template = lambda *_: "print('{{NAME}}')"
    path = gen.generate_integration_ready_code("Obj")
    assert path.exists()

    with sqlite3.connect(prod_db) as conn:
        try:
            tracking = conn.execute("SELECT COUNT(*) FROM script_tracking").fetchone()[0]
        except sqlite3.Error:
            tracking = 0
        try:
            enhanced = conn.execute("SELECT COUNT(*) FROM enhanced_script_tracking").fetchone()[0]
        except sqlite3.Error:
            enhanced = 0

    assert tracking == 1 and enhanced == 1


def test_integration_ready_rollback_on_failure(tmp_path: Path, monkeypatch) -> None:
    prod_db = tmp_path / "production.db"
    doc_db = tmp_path / "documentation.db"
    tpl_db = tmp_path / "template.db"
    analytics = tmp_path / "databases" / "analytics.db"
    analytics.parent.mkdir()

    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"
    with sqlite3.connect(prod_db) as conn:
        conn.execute(
            "CREATE TABLE template_placeholders (placeholder_name TEXT, default_value TEXT)"
        )
        conn.execute("INSERT INTO template_placeholders VALUES ('{{NAME}}', 'World')")

    def fake_log(event: dict, *, table: str, db_path: Path, **_: object) -> None:
        with sqlite3.connect(db_path) as conn:
            conn.execute(f"CREATE TABLE IF NOT EXISTS {table} (event TEXT)")
            conn.execute(f"INSERT INTO {table} (event) VALUES (?)", (event.get("event"),))
            conn.commit()

    monkeypatch.setattr(dbgen, "_log_event", fake_log)
    monkeypatch.setattr(dbgen.DBFirstCodeGenerator, "generate", lambda self, *_: "print('{{NAME}}')")
    monkeypatch.setattr(Path, "write_text", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("fail")))

    gen = DBFirstCodeGenerator(prod_db, doc_db, tpl_db, analytics)
    with pytest.raises(RuntimeError):
        gen.generate_integration_ready_code("Obj")

    assert not (tmp_path / "Obj.py").exists()
    with sqlite3.connect(prod_db) as conn:
        try:
            tracking = conn.execute("SELECT COUNT(*) FROM script_tracking").fetchone()[0]
        except sqlite3.Error:
            tracking = 0
        try:
            enhanced = conn.execute("SELECT COUNT(*) FROM enhanced_script_tracking").fetchone()[0]
        except sqlite3.Error:
            enhanced = 0
    with sqlite3.connect(analytics) as conn:
        fails = conn.execute(
            "SELECT COUNT(*) FROM generator_events WHERE event='integration_ready_failed'"
        ).fetchone()[0]

    assert tracking == 0 and enhanced == 0 and fails == 1
