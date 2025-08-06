import hashlib
import json
import logging
import sqlite3

from scripts.database.template_asset_ingestor import ingest_templates
from scripts.database.unified_database_initializer import initialize_database


def test_duplicate_logging_and_analytics(tmp_path, caplog, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    workspace = tmp_path
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    db_dir = workspace / "databases"
    db_dir.mkdir()
    db_path = db_dir / "enterprise_assets.db"
    initialize_database(db_path)
    templates_dir = workspace / "prompts"
    templates_dir.mkdir()
    content = "Sample"
    template_file = templates_dir / "sample.md"
    template_file.write_text(content)

    ingest_templates(workspace, templates_dir)

    caplog.set_level(logging.INFO)
    ingest_templates(workspace, templates_dir)

    digest = hashlib.sha256(content.encode()).hexdigest()
    messages = [json.loads(m) for m in caplog.messages if m.startswith("{")]
    event = next(m for m in messages if m.get("template_hash") == digest)
    assert event["status"] == "DUPLICATE"
    assert event["db_path"] == str(db_path)

    analytics_db = db_dir / "analytics.db"
    with sqlite3.connect(analytics_db) as conn:
        rows = conn.execute(
            "SELECT details FROM event_log WHERE description='template_dedup_summary'"
        ).fetchall()
    assert rows
    summary = json.loads(rows[-1][0])
    assert summary["duplicates"] >= 1
    assert summary["db_path"] == str(db_path)
