import hashlib
import logging
import os
import sqlite3
from pathlib import Path

from scripts.database.template_asset_ingestor import ingest_templates
from scripts.database.unified_database_initializer import initialize_database
from template_engine.learning_templates import get_lesson_templates


def test_ingest_templates(tmp_path: Path) -> None:
    workspace = tmp_path
    os.environ["GH_COPILOT_WORKSPACE"] = str(workspace)
    db_dir = workspace / "databases"
    db_dir.mkdir()
    db_path = db_dir / "enterprise_assets.db"
    initialize_database(db_path)
    templates_dir = workspace / "prompts"
    templates_dir.mkdir()
    temp_file = templates_dir / "sample.md"
    temp_file.write_text("Sample template")
    ingest_templates(workspace, templates_dir)
    with sqlite3.connect(db_path) as conn:
        t_count = conn.execute("SELECT COUNT(*) FROM template_assets").fetchone()[0]
        p_count = conn.execute("SELECT COUNT(*) FROM pattern_assets").fetchone()[0]
        lesson_count = conn.execute(
            "SELECT COUNT(*) FROM pattern_assets WHERE lesson_name IS NOT NULL"
        ).fetchone()[0]
    expected_lessons = len(get_lesson_templates())
    assert t_count == 1
    assert p_count == 1 + expected_lessons
    assert lesson_count == expected_lessons


def test_duplicate_templates_skipped(tmp_path: Path) -> None:
    workspace = tmp_path
    os.environ["GH_COPILOT_WORKSPACE"] = str(workspace)
    db_dir = workspace / "databases"
    db_dir.mkdir()
    db_path = db_dir / "enterprise_assets.db"
    initialize_database(db_path)
    templates_dir = workspace / "prompts"
    templates_dir.mkdir()
    (templates_dir / "a.md").write_text("Sample")
    (templates_dir / "b.md").write_text("Sample")
    ingest_templates(workspace, templates_dir)
    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM template_assets").fetchone()[0]
    assert count == 1


def test_reingest_template_logs_duplicate(tmp_path: Path, caplog, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    workspace = tmp_path
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    db_dir = workspace / "databases"
    db_dir.mkdir()
    db_path = db_dir / "enterprise_assets.db"
    initialize_database(db_path)
    templates_dir = workspace / "prompts"
    templates_dir.mkdir()
    temp_file = templates_dir / "sample.md"
    content = "Sample"
    temp_file.write_text(content)
    ingest_templates(workspace, templates_dir)
    caplog.clear()
    caplog.set_level(logging.INFO)
    ingest_templates(workspace, templates_dir)
    digest = hashlib.sha256(content.encode()).hexdigest()
    messages = " ".join(caplog.messages)
    assert digest in messages
    assert str(temp_file) in messages
    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM template_assets").fetchone()[0]
    assert count == 1
