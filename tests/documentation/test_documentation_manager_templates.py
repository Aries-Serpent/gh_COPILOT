"""Functional tests for the documentation manager template selection."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from archive.consolidated_scripts import enterprise_database_driven_documentation_manager as mgr


def _create_production_db(db: Path, content: str) -> None:
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE documentation (title TEXT, content TEXT, compliance_score INTEGER)")
        conn.execute(
            "INSERT INTO documentation VALUES ('Doc1', ?, 80)",
            (content,),
        )
        conn.execute(
            "CREATE TABLE template_repository (template_name TEXT, template_category TEXT, template_content TEXT, success_rate REAL)"
        )
        conn.execute("INSERT INTO template_repository VALUES ('Doc1', 'cat', 'prod', 0.9)")


def _create_doc_db(db: Path, template: str) -> None:
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE documentation_templates (template_id TEXT, template_name TEXT, template_type TEXT, template_content TEXT)"
        )
        conn.execute(
            "INSERT INTO documentation_templates VALUES ('1', 'Doc1', 'cat', ?)",
            (template,),
        )


def test_template_selection_from_documentation_db(tmp_path: Path) -> None:
    prod_db = tmp_path / "production.db"
    doc_db = tmp_path / "documentation.db"
    analytics = tmp_path / "databases" / "analytics.db"
    analytics.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics) as conn:
        conn.execute("CREATE TABLE render_events (event TEXT, title TEXT, timestamp TEXT)")
    out_dir = tmp_path / "render"
    mgr.RENDER_LOG_DIR = out_dir
    mgr.LOG_FILE = out_dir / "log.log"
    out_dir.mkdir(parents=True, exist_ok=True)

    _create_production_db(prod_db, "orig")
    _create_doc_db(doc_db, "doc-template")

    # ensure workspace points to tmp_path to avoid recursive check failures
    import os

    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    os.environ["GH_COPILOT_BACKUP_ROOT"] = str(tmp_path / "backups")

    class StubGen:
        def __init__(self, *args, **kwargs):
            pass

        def select_best_template(self, *_: str) -> str:
            return ""

    mgr.TemplateAutoGenerator = StubGen

    manager = mgr.DocumentationManager(
        database=prod_db,
        documentation_db=doc_db,
        analytics_db=analytics,
        completion_db=tmp_path / "completion.db",
        dashboard_dir=tmp_path / "dashboard",
    )

    count = manager.render()
    md_file = out_dir / "Doc1.md"
    assert count == 1
    assert md_file.read_text() == "doc-template"

    with sqlite3.connect(analytics) as conn:
        rows = conn.execute("SELECT title FROM render_events").fetchall()
    assert rows == [("Doc1",)]

    dashboard_file = manager.dashboard_dir / "metrics.json"
    assert dashboard_file.exists()
