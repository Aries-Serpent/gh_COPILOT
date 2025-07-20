import sqlite3
from pathlib import Path

from scripts.database.documentation_ingestor import ingest_documentation


def test_ingest_documentation(tmp_path: Path) -> None:
    workspace = tmp_path
    db_dir = workspace / "databases"
    db_dir.mkdir()
    db_path = db_dir / "enterprise_assets.db"
    docs_dir = workspace / "documentation"
    docs_dir.mkdir()
    doc = docs_dir / "guide.md"
    doc.write_text("# Guide")
    ingest_documentation(workspace, docs_dir)
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT doc_path, modified_at FROM documentation_assets"
        ).fetchone()
        ops = conn.execute(
            "SELECT COUNT(*) FROM cross_database_sync_operations"
        ).fetchone()[0]
    assert row[0].endswith("guide.md")
    assert row[1] is not None
    assert ops == 1


def test_zero_byte_file_skipped(tmp_path: Path) -> None:
    workspace = tmp_path
    db_dir = workspace / "databases"
    db_dir.mkdir()
    docs_dir = workspace / "documentation"
    docs_dir.mkdir()
    (docs_dir / "empty.md").write_text("")
    ingest_documentation(workspace, docs_dir)
    db_path = db_dir / "enterprise_assets.db"
    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM documentation_assets").fetchone()[0]
        ops = conn.execute(
            "SELECT COUNT(*) FROM cross_database_sync_operations"
        ).fetchone()[0]
    assert count == 0
    assert ops == 1


def test_missing_directory(tmp_path: Path) -> None:
    workspace = tmp_path
    db_dir = workspace / "databases"
    db_dir.mkdir()
    docs_dir = workspace / "missing"
    ingest_documentation(workspace, docs_dir)
    db_path = db_dir / "enterprise_assets.db"
    with sqlite3.connect(db_path) as conn:
        ops = conn.execute(
            "SELECT COUNT(*) FROM cross_database_sync_operations"
        ).fetchone()[0]
        count = conn.execute("SELECT COUNT(*) FROM documentation_assets").fetchone()[0]
    assert ops == 1
    assert count == 0
