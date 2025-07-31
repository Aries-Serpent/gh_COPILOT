import sqlite3
from pathlib import Path

from scripts.database.unified_database_initializer import initialize_database
from scripts.automation.setup_ingest_audit import ingest_assets


def test_ingest_assets(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path.parent / "backups"))

    docs_dir = tmp_path / "documentation"
    docs_dir.mkdir()
    (docs_dir / "doc.md").write_text("# doc")

    templates_dir = tmp_path / "prompts"
    templates_dir.mkdir()
    (templates_dir / "temp.md").write_text("template")

    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    db_path = db_dir / "enterprise_assets.db"
    initialize_database(db_path)

    ingest_assets(tmp_path)

    with sqlite3.connect(db_path) as conn:
        doc_count = conn.execute("SELECT COUNT(*) FROM documentation_assets").fetchone()[0]
        template_count = conn.execute("SELECT COUNT(*) FROM template_assets").fetchone()[0]
        pattern_count = conn.execute("SELECT COUNT(*) FROM pattern_assets").fetchone()[0]
        ops_count = conn.execute("SELECT COUNT(*) FROM cross_database_sync_operations").fetchone()[0]

    assert doc_count == 1
    assert template_count == 1
    assert pattern_count == 1
    # two records from database initialization and one each from docs/templates
    assert ops_count == 4
