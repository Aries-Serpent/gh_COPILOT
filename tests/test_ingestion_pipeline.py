import sqlite3
from pathlib import Path

from scripts.database.template_asset_ingestor import ingest_templates
from scripts.database.documentation_ingestor import ingest_documentation
from scripts.database.cross_database_sync_logger import _table_exists, log_sync_operation
from scripts.database.ingestion_validator import IngestionValidator


def _create_duplicate_files(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "first.md").write_text("duplicate", encoding="utf-8")
    (directory / "second.md").write_text("duplicate", encoding="utf-8")


def test_ingestion_pipeline(tmp_path, monkeypatch):
    workspace = tmp_path
    db_dir = workspace / "databases"
    prompts_dir = workspace / "prompts"
    docs_dir = workspace / "documentation"
    _create_duplicate_files(prompts_dir)
    _create_duplicate_files(docs_dir)

    analytics_db = db_dir / "analytics.db"
    monkeypatch.setenv("ANALYTICS_DB", str(analytics_db))
    monkeypatch.setenv("TEST_MODE", "1")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))

    ingest_templates(workspace, prompts_dir)
    ingest_documentation(workspace, docs_dir)
    db_path = db_dir / "enterprise_assets.db"

    with sqlite3.connect(analytics_db) as conn:
        assert _table_exists(conn, "event_log")
        event_count_before = conn.execute(
            "SELECT COUNT(*) FROM event_log"
        ).fetchone()[0]

    log_sync_operation(db_path, "manual_operation", status="MANUAL")

    with sqlite3.connect(db_path) as conn:
        template_count = conn.execute(
            "SELECT COUNT(*) FROM template_assets"
        ).fetchone()[0]
        doc_count = conn.execute(
            "SELECT COUNT(*) FROM documentation_assets"
        ).fetchone()[0]
        statuses = {
            row[0]
            for row in conn.execute(
                "SELECT status FROM cross_database_sync_operations"
            ).fetchall()
        }
        assert _table_exists(conn, "cross_database_sync_operations")

    assert template_count == 1
    assert doc_count == 1
    assert {"DUPLICATE", "SUCCESS", "MANUAL"}.issubset(statuses)

    with sqlite3.connect(analytics_db) as conn:
        event_count_after = conn.execute(
            "SELECT COUNT(*) FROM event_log"
        ).fetchone()[0]
    assert event_count_after == event_count_before + 1

    validator = IngestionValidator(workspace, db_path, analytics_db)
    assert validator.validate() is True
