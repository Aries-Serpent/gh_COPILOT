import sqlite3

from scripts.database.template_asset_ingestor import ingest_templates


def test_duplicate_status_and_deduplication(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    workspace = tmp_path
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    db_dir = workspace / "databases"
    db_dir.mkdir()
    analytics_db = db_dir / "analytics.db"
    monkeypatch.setenv("ANALYTICS_DB", str(analytics_db))
    templates_dir = workspace / "prompts"
    templates_dir.mkdir()
    template = templates_dir / "example.md"
    template.write_text("Hello")

    ingest_templates(workspace, templates_dir)
    ingest_templates(workspace, templates_dir)

    db_path = db_dir / "enterprise_assets.db"
    with sqlite3.connect(db_path) as conn:
        dup = conn.execute(
            "SELECT COUNT(*) FROM cross_database_sync_operations WHERE operation=? AND status=?",
            ("template_ingestion", "DUPLICATE"),
        ).fetchone()[0]
        assert dup == 1
        count = conn.execute("SELECT COUNT(*) FROM template_assets").fetchone()[0]
        assert count == 1
