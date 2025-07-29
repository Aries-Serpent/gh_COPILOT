import sqlite3
from pathlib import Path

from scripts.documentation.enterprise_documentation_manager import (
    EnterpriseDocumentationManager,
)
from template_engine.auto_generator import TemplateAutoGenerator
from utils import log_utils


def create_template_dbs(tmp_path: Path):
    analytics_db = tmp_path / "databases" / "analytics.db"
    analytics_db.parent.mkdir(exist_ok=True)
    completion_db = tmp_path / "template_completion.db"
    with sqlite3.connect(analytics_db) as conn:
        conn.execute("CREATE TABLE ml_pattern_optimization (replacement_template TEXT)")
        conn.execute("INSERT INTO ml_pattern_optimization VALUES ('{content}')")
        conn.execute("CREATE TABLE compliance_rules (pattern TEXT)")
        conn.execute("INSERT INTO compliance_rules VALUES ('bad')")
    with sqlite3.connect(completion_db) as conn:
        conn.execute("CREATE TABLE templates (template_content TEXT)")
        conn.execute("INSERT INTO templates VALUES ('{content}')")
    return analytics_db, completion_db


def test_generate_files(tmp_path, monkeypatch):
    workspace = tmp_path
    db_dir = workspace / "databases"
    doc_dir = workspace / "documentation"
    db_dir.mkdir()
    doc_dir.mkdir()
    db_path = db_dir / "documentation.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE enterprise_documentation (doc_id TEXT, doc_type TEXT, content TEXT)")
        conn.executemany(
            "INSERT INTO enterprise_documentation VALUES (?,?,?)",
            [("1", "README", "alpha"), ("2", "README", "beta")],
        )
    analytics_db, completion_db = create_template_dbs(tmp_path)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("DOCUMENTATION_DB_PATH", str(db_path))
    manager = EnterpriseDocumentationManager(
        workspace=workspace,
        db_path=db_path,
        analytics_db=analytics_db,
        completion_db=completion_db,
    )
    files = manager.generate_files("README")
    assert len(files) == 2
    for f in files:
        assert f.exists()
        assert f.read_text() in {"alpha", "beta"}


def test_generate_files_records_status(tmp_path, monkeypatch):
    workspace = tmp_path
    db_dir = workspace / "databases"
    doc_dir = workspace / "documentation"
    db_dir.mkdir()
    doc_dir.mkdir()
    doc_db = db_dir / "documentation.db"
    prod_db = db_dir / "production.db"
    prod_db.touch()
    with sqlite3.connect(doc_db) as conn:
        conn.execute("CREATE TABLE enterprise_documentation (doc_id TEXT, doc_type TEXT, content TEXT)")
        conn.executemany(
            "INSERT INTO enterprise_documentation VALUES (?,?,?)",
            [("1", "README", "alpha"), ("2", "README", "beta")],
        )

    analytics_db, completion_db = create_template_dbs(tmp_path)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("DOCUMENTATION_DB_PATH", str(doc_db))
    manager = EnterpriseDocumentationManager(
        workspace=workspace,
        db_path=doc_db,
        analytics_db=analytics_db,
        completion_db=completion_db,
    )

    manager.generate_files("README")

    with sqlite3.connect(prod_db) as conn:
        rows = conn.execute("SELECT doc_id, path FROM documentation_status ORDER BY doc_id").fetchall()

    assert rows == [
        ("1", str(workspace / "documentation" / "generated" / "enterprise_docs" / "1.md")),
        ("2", str(workspace / "documentation" / "generated" / "enterprise_docs" / "2.md")),
    ]


def test_compliance_scores_logged_and_non_compliant_skipped(tmp_path, monkeypatch):
    workspace = tmp_path
    db_dir = workspace / "databases"
    doc_dir = workspace / "documentation"
    db_dir.mkdir()
    doc_dir.mkdir()
    doc_db = db_dir / "documentation.db"
    prod_db = db_dir / "production.db"
    prod_db.touch()
    with sqlite3.connect(doc_db) as conn:
        conn.execute("CREATE TABLE enterprise_documentation (doc_id TEXT, doc_type TEXT, content TEXT)")
        conn.executemany(
            "INSERT INTO enterprise_documentation VALUES (?,?,?)",
            [
                ("1", "README", "good"),
                ("2", "README", "bad sample"),
            ],
        )

    analytics_db, completion_db = create_template_dbs(tmp_path)
    events: list[dict] = []
    def fake_log(evt, **_):
        events.append(evt)

    monkeypatch.setattr(log_utils, "_log_event", fake_log)
    monkeypatch.setattr(
        "scripts.documentation.enterprise_documentation_manager._log_event",
        fake_log,
    )
    monkeypatch.setattr(
        "template_engine.template_synchronizer.ANALYTICS_DB",
        analytics_db,
        raising=False,
    )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("DOCUMENTATION_DB_PATH", str(doc_db))
    manager = EnterpriseDocumentationManager(
        workspace=workspace,
        db_path=doc_db,
        analytics_db=analytics_db,
        completion_db=completion_db,
    )

    files = manager.generate_files("README")
    assert len(files) == 1
    assert files[0].name == "1.md"
    scores = {e["doc_id"]: e["compliance_score"] for e in events if e.get("event") == "doc_generated"}
    assert scores["1"] > scores["2"]
