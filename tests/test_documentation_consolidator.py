#!/usr/bin/env python3
import os
import shutil
import sqlite3
from pathlib import Path




def _prepare_db(src: Path, dest: Path) -> None:
    shutil.copy(src, dest)
    with sqlite3.connect(dest) as conn:
        conn.execute(
            "INSERT INTO enterprise_documentation "
            "(doc_id, doc_type, title, content, source_path) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                "backup1",
                "BACKUP_LOG",
                "Backup",
                "data",
                str(Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd())) / "backups" / "tmp.bak"),
            ),
        )
        conn.execute(
            "INSERT INTO enterprise_documentation "
            "(doc_id, doc_type, title, content, source_path) "
            "VALUES (?, ?, ?, ?, ?)",
            ("dup1", "README", "Duplicate", "# doc", "file1.md"),
        )
        conn.execute(
            "INSERT INTO enterprise_documentation "
            "(doc_id, doc_type, title, content, source_path) "
            "VALUES (?, ?, ?, ?, ?)",
            ("dup2", "README", "Duplicate", "# doc2", "file2.md"),
        )


def test_documentation_consolidator(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[1]
    workspace = tmp_path
    db_dir = workspace / "databases"
    doc_dir = workspace / "documentation"
    db_dir.mkdir()
    doc_dir.mkdir()
    _prepare_db(repo_root / "databases" / "documentation.db", db_dir / "documentation.db")
    shutil.copy(repo_root / "documentation" / "README.md", doc_dir / "README.md")

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("DOCUMENTATION_DB_PATH", str(db_dir / "documentation.db"))
    analytics_db = tmp_path / "analytics.db"
    monkeypatch.setenv("ANALYTICS_DB", str(analytics_db))
    import importlib
    consolidate = importlib.import_module("scripts.documentation_consolidator").consolidate
    consolidate()

    with sqlite3.connect(db_dir / "documentation.db") as conn:
        cur = conn.execute(
            "SELECT COUNT(*) FROM enterprise_documentation "
            "WHERE source_path LIKE '%backup%' OR doc_type='BACKUP_LOG'"
        )
        assert cur.fetchone()[0] == 0

        cur = conn.execute(
            "SELECT COUNT(*) FROM enterprise_documentation "
            "WHERE title='Duplicate'"
        )
        assert cur.fetchone()[0] == 1

        cur = conn.execute("SELECT COUNT(*) FROM documentation_templates")
        assert cur.fetchone()[0] > 0

        cur = conn.execute("SELECT COUNT(*) FROM template_registry")
        assert cur.fetchone()[0] > 0

    assert (doc_dir / "generated" / "feature_matrix.csv").exists()
    assert (doc_dir / "generated" / "feature_matrix.md").exists()
    assert (doc_dir / "generated" / "feature_matrix.json").exists()

    with sqlite3.connect(analytics_db) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM audit_log")
        assert cur.fetchone()[0] >= 2
