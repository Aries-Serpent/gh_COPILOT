import json
import os
import sqlite3
from pathlib import Path

import template_engine.db_first_code_generator as dbgen
from template_engine.db_first_code_generator import DBFirstCodeGenerator


def test_progress_and_requirement_mapping_logged(tmp_path: Path) -> None:
    prod_db = tmp_path / "production.db"
    doc_db = tmp_path / "documentation.db"
    tpl_db = tmp_path / "template.db"
    analytics = tmp_path / "analytics.db"

    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"

    with sqlite3.connect(prod_db) as conn:
        conn.execute(
            "CREATE TABLE template_placeholders (placeholder_name TEXT, default_value TEXT)"
        )
        conn.execute("INSERT INTO template_placeholders VALUES ('{{NAME}}', 'World')")

    def fake_log(event: dict, *, table: str, db_path: Path, **_: object) -> None:
        with sqlite3.connect(db_path) as conn:
            conn.execute(f"CREATE TABLE IF NOT EXISTS {table} (data TEXT)")
            conn.execute(
                f"INSERT INTO {table} (data) VALUES (?)",
                (json.dumps(event),),
            )
            conn.commit()

    dbgen._log_event = fake_log

    gen = DBFirstCodeGenerator(prod_db, doc_db, tpl_db, analytics)

    def select_template(*_: object) -> str:
        return "print('{{NAME}}')"

    gen.select_best_template = select_template

    path = gen.generate_integration_ready_code("REQ-1")
    assert path.exists()

    with sqlite3.connect(analytics) as conn:
        events = [json.loads(r[0]) for r in conn.execute("SELECT data FROM generator_events")]

    phases = {e.get("phase") for e in events if e.get("event") == "integration_progress"}
    assert phases == {"template_selection", "token_replacement", "file_write"}

    tpl_evt = next(e for e in events if e.get("event") == "template_selected")
    assert tpl_evt["requirement_map"]["REQ-1"].startswith("print")

    token_evt = next(e for e in events if e.get("event") == "tokens_replaced")
    assert token_evt["requirement_map"]["REQ-1"].startswith("print")

    mapping_event = next(e for e in events if e.get("event") == "requirement_mapping")
    assert mapping_event["mapping"]["REQ-1"]["path"] == str(path)

    generated_event = next(
        e for e in events if e.get("event") == "integration_ready_generated"
    )
    assert generated_event["requirement_map"]["REQ-1"] == str(path)

