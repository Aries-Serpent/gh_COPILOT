"""Tests for :mod:`scripts.autonomous_setup_and_audit`."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from scripts.autonomous_setup_and_audit import ingest_assets
from scripts.database.unified_database_initializer import initialize_database


def test_ingest_assets_populates_db(tmp_path: Path, monkeypatch) -> None:
    """``ingest_assets`` should load sample files into the database."""

    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))
    monkeypatch.chdir(tmp_path)

    docs_dir = tmp_path / "documentation"
    docs_dir.mkdir()
    (docs_dir / "doc.md").write_text("# doc")

    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    (templates_dir / "template.md").write_text("template body")

    db_path = tmp_path / "production.db"
    initialize_database(db_path)

    ingest_assets(docs_dir, templates_dir, db_path)

    with sqlite3.connect(db_path) as conn:
        doc_count = conn.execute("SELECT COUNT(*) FROM documentation_assets").fetchone()[0]
        template_count = conn.execute("SELECT COUNT(*) FROM template_assets").fetchone()[0]
        pattern_count = conn.execute("SELECT COUNT(*) FROM pattern_assets").fetchone()[0]

    assert doc_count == 1
    assert template_count == 1
    assert pattern_count == 1
