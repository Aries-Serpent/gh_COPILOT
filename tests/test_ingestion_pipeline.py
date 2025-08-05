import sqlite3

import pytest

from scripts.database import template_asset_ingestor as tai
from scripts.database import documentation_ingestor as di
from scripts.database.cross_database_sync_logger import _table_exists
from scripts.database.ingestion_validator import IngestionValidator


@pytest.fixture()
def temp_workspace(tmp_path, monkeypatch):
    workspace = tmp_path
    (workspace / "prompts").mkdir()
    (workspace / "documentation").mkdir()
    (workspace / "databases").mkdir()

    monkeypatch.setattr(tai, "validate_enterprise_operation", lambda *a, **k: True)
    monkeypatch.setattr(di, "validate_enterprise_operation", lambda *a, **k: True)
    monkeypatch.setattr("scripts.database.cross_database_sync_logger.validate_enterprise_operation", lambda *a, **k: True)
    monkeypatch.setattr(tai, "get_dataset_sources", lambda w: [])
    monkeypatch.setattr(tai, "get_lesson_templates", lambda: {})

    class DummyValidator:
        def validate_corrections(self, paths):
            return None

    monkeypatch.setattr(di, "SecondaryCopilotValidator", lambda: DummyValidator())
    monkeypatch.setenv("ANALYTICS_DB", str(workspace / "databases" / "analytics.db"))
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    return workspace


def _read_table(conn, table):
    return [row for row in conn.execute(f"SELECT * FROM {table}")]


def test_ingestion_pipeline(temp_workspace):
    workspace = temp_workspace
    tmpl_dir = workspace / "prompts"
    doc_dir = workspace / "documentation"

    (tmpl_dir / "a.md").write_text("template")
    (tmpl_dir / "b.md").write_text("template")  # duplicate
    (doc_dir / "a.md").write_text("doc")
    (doc_dir / "b.md").write_text("doc")  # duplicate

    tai.ingest_templates(workspace)
    di.ingest_documentation(workspace)

    db_path = workspace / "databases" / "enterprise_assets.db"
    analytics_db = workspace / "databases" / "analytics.db"

    with sqlite3.connect(db_path) as conn:
        templates = _read_table(conn, "template_assets")
        docs = _read_table(conn, "documentation_assets")
        sync_logs = _read_table(conn, "cross_database_sync_operations")
        assert _table_exists(conn, "cross_database_sync_operations")

    with sqlite3.connect(analytics_db) as conn:
        events = _read_table(conn, "event_log")

    assert len(templates) == 1
    assert len(docs) == 1
    statuses = {row[2] for row in sync_logs}
    assert {"SUCCESS", "DUPLICATE"}.issubset(statuses)
    assert events, "Analytics log should not be empty"

    validator = IngestionValidator(workspace, db_path, analytics_db)
    assert validator.validate()
