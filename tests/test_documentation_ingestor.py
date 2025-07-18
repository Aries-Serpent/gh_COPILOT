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
        count = conn.execute("SELECT COUNT(*) FROM documentation_assets").fetchone()[0]
    assert count == 1
