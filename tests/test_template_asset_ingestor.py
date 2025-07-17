import sqlite3
from pathlib import Path

from scripts.database.template_asset_ingestor import ingest_templates
from scripts.database.unified_database_initializer import initialize_database


def test_ingest_templates(tmp_path: Path) -> None:
    workspace = tmp_path
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
    assert t_count == 1
    assert p_count == 1
