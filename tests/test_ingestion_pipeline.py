import hashlib
import sqlite3
from datetime import datetime, timezone
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
    db_dir.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """
            CREATE TABLE event_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                module TEXT,
                level TEXT,
                doc_path TEXT,
                status TEXT,
                sha256 TEXT,
                md5 TEXT,
                description TEXT
            )
            """
        )
    monkeypatch.setenv("ANALYTICS_DB", str(analytics_db))
    monkeypatch.setenv("TEST_MODE", "1")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))

    ingest_templates(workspace, prompts_dir)
    ingest_documentation(workspace, docs_dir)
    db_path = db_dir / "enterprise_assets.db"

    digest = hashlib.sha256("duplicate".encode()).hexdigest()
    rel_doc2 = str((docs_dir / "second.md").relative_to(workspace))
    with sqlite3.connect(analytics_db) as conn:
        assert _table_exists(conn, "event_log")
        duplicate_rows = conn.execute(
            "SELECT doc_path, sha256 FROM event_log WHERE status='DUPLICATE' AND module='documentation_ingestor'",
        ).fetchall()
        event_count_before = conn.execute(
            "SELECT COUNT(*) FROM event_log",
        ).fetchone()[0]
    assert duplicate_rows == [(rel_doc2, digest)]

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


def test_cross_db_duplicate_detection(tmp_path: Path, monkeypatch) -> None:
    workspace = tmp_path
    db_dir = workspace / "databases"
    prompts_dir = workspace / "prompts"
    docs_dir = workspace / "documentation"
    _create_duplicate_files(prompts_dir)
    _create_duplicate_files(docs_dir)

    analytics_db = db_dir / "analytics.db"
    db_dir.mkdir()
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """
            CREATE TABLE event_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                module TEXT,
                level TEXT,
                doc_path TEXT,
                status TEXT,
                sha256 TEXT,
                md5 TEXT
            )
            """
        )

    digest = hashlib.sha256("duplicate".encode()).hexdigest()
    prod_db = db_dir / "production.db"
    now = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(prod_db) as conn:
        conn.execute(
            "CREATE TABLE template_assets (id INTEGER PRIMARY KEY, template_path TEXT NOT NULL, content_hash TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL)"
        )
        conn.execute(
            "CREATE TABLE documentation_assets (id INTEGER PRIMARY KEY, doc_path TEXT NOT NULL, content_hash TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL, modified_at TEXT NOT NULL)"
        )
        conn.execute(
            "INSERT INTO template_assets (template_path, content_hash, created_at) VALUES (?, ?, ?)",
            ("existing_template.md", digest, now),
        )
        conn.execute(
            "INSERT INTO documentation_assets (doc_path, content_hash, created_at, modified_at) VALUES (?, ?, ?, ?)",
            ("existing_doc.md", digest, now, now),
        )

    monkeypatch.setenv("ANALYTICS_DB", str(analytics_db))
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("TEST_MODE", "1")
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")

    ingest_templates(workspace, prompts_dir)
    ingest_documentation(workspace, docs_dir)

    db_path = db_dir / "enterprise_assets.db"
    with sqlite3.connect(db_path) as conn:
        doc_count = conn.execute("SELECT COUNT(*) FROM documentation_assets").fetchone()[0]
        dup_count = conn.execute(
            "SELECT COUNT(*) FROM cross_database_sync_operations WHERE operation='documentation_ingestion' AND status='DUPLICATE'"
        ).fetchone()[0]

    assert doc_count == 0
    assert dup_count == 2

    rel_doc1 = str((docs_dir / "first.md").relative_to(workspace))
    rel_doc2 = str((docs_dir / "second.md").relative_to(workspace))
    with sqlite3.connect(analytics_db) as conn:
        rows = conn.execute(
            "SELECT doc_path, sha256 FROM event_log WHERE status='DUPLICATE' AND module='documentation_ingestor'"
        ).fetchall()
    assert set(rows) == {(rel_doc1, digest), (rel_doc2, digest)}
