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
        conn.execute(
            """
            CREATE TABLE correction_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event TEXT,
                doc_id TEXT,
                compliance_score REAL,
                timestamp TEXT,
                module TEXT,
                level TEXT,
                path TEXT,
                asset_type TEXT
            )
            """
        )
        conn.execute(
            "CREATE TABLE cross_link_events (id INTEGER PRIMARY KEY AUTOINCREMENT, file_path TEXT NOT NULL, linked_path TEXT NOT NULL, timestamp TEXT NOT NULL, module TEXT, level TEXT)"
        )
        conn.execute(
            "CREATE TABLE cross_link_summary (id INTEGER PRIMARY KEY AUTOINCREMENT, actions INTEGER, links INTEGER, timestamp TEXT NOT NULL, module TEXT, level TEXT)"
        )
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
        conn.execute(
            "CREATE TABLE enterprise_documentation (doc_id TEXT, doc_type TEXT, content TEXT, source_path TEXT)"
        )
        conn.executemany(
            "INSERT INTO enterprise_documentation VALUES (?,?,?,?)",
            [("1", "README", "alpha", "src/1.py"), ("2", "README", "beta", "src/2.py")],
        )
    analytics_db, completion_db = create_template_dbs(tmp_path)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("DOCUMENTATION_DB_PATH", str(db_path))
    monkeypatch.setattr(TemplateAutoGenerator, "select_best_template", lambda *a, **k: "{content}")
    monkeypatch.setattr(EnterpriseDocumentationManager, "calculate_compliance", lambda *a, **k: 100.0)
    manager = EnterpriseDocumentationManager(
        workspace=workspace,
        db_path=db_path,
        analytics_db=analytics_db,
        completion_db=completion_db,
    )
    files = manager.generate_files("README", output_formats=("md", "html", "pdf"))
    assert len(files) == 6
    for f in files:
        assert f.exists()
    pdfs = [p for p in files if p.suffix == ".pdf"]
    for pdf in pdfs:
        data = pdf.read_bytes()
        assert data.startswith(b"%PDF"), "PDF header missing"
        assert len(data) > 0


def test_pdf_also_generates_markdown(tmp_path, monkeypatch):
    workspace = tmp_path
    db_dir = workspace / "databases"
    doc_dir = workspace / "documentation"
    db_dir.mkdir()
    doc_dir.mkdir()
    db_path = db_dir / "documentation.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE enterprise_documentation (doc_id TEXT, doc_type TEXT, content TEXT, source_path TEXT)"
        )
        conn.execute(
            "INSERT INTO enterprise_documentation VALUES (?,?,?,?)",
            ("1", "README", "# Heading\nAlpha", "src/1.py"),
        )
    analytics_db, completion_db = create_template_dbs(tmp_path)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("DOCUMENTATION_DB_PATH", str(db_path))
    monkeypatch.setattr(TemplateAutoGenerator, "select_best_template", lambda *a, **k: "{content}")
    monkeypatch.setattr(EnterpriseDocumentationManager, "calculate_compliance", lambda *a, **k: 100.0)
    manager = EnterpriseDocumentationManager(
        workspace=workspace,
        db_path=db_path,
        analytics_db=analytics_db,
        completion_db=completion_db,
    )
    files = manager.generate_files("README", output_formats=("pdf",))
    pdf_path = workspace / "documentation" / "generated" / "enterprise_docs" / "1.pdf"
    md_path = workspace / "documentation" / "generated" / "enterprise_docs" / "1.md"
    assert pdf_path in files
    assert md_path in files
    md_text = md_path.read_text(encoding="utf-8")
    assert "# Heading" in md_text


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
        conn.execute(
            "CREATE TABLE enterprise_documentation (doc_id TEXT, doc_type TEXT, content TEXT, source_path TEXT)"
        )
        conn.executemany(
            "INSERT INTO enterprise_documentation VALUES (?,?,?,?)",
            [("1", "README", "alpha", "src/1.py"), ("2", "README", "beta", "src/2.py")],
        )

    analytics_db, completion_db = create_template_dbs(tmp_path)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("DOCUMENTATION_DB_PATH", str(doc_db))
    monkeypatch.setattr(TemplateAutoGenerator, "select_best_template", lambda *a, **k: "{content}")
    monkeypatch.setattr(EnterpriseDocumentationManager, "calculate_compliance", lambda *a, **k: 100.0)
    manager = EnterpriseDocumentationManager(
        workspace=workspace,
        db_path=doc_db,
        analytics_db=analytics_db,
        completion_db=completion_db,
    )

    manager.generate_files("README", output_formats=("md", "html", "pdf"))

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
        conn.execute(
            "CREATE TABLE enterprise_documentation (doc_id TEXT, doc_type TEXT, content TEXT, source_path TEXT)"
        )
        conn.executemany(
            "INSERT INTO enterprise_documentation VALUES (?,?,?,?)",
            [
                ("1", "README", "good", "src/1.py"),
                ("2", "README", "bad sample", "src/2.py"),
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
    monkeypatch.setattr(TemplateAutoGenerator, "select_best_template", lambda *a, **k: "{content}")
    monkeypatch.setattr(EnterpriseDocumentationManager, "calculate_compliance", lambda *a, **k: 100.0)
    manager = EnterpriseDocumentationManager(
        workspace=workspace,
        db_path=doc_db,
        analytics_db=analytics_db,
        completion_db=completion_db,
    )

    files = manager.generate_files("README", output_formats=("md", "html", "pdf"))
    assert len(files) == 6
    assert any(f.name == "1.md" for f in files)


def test_generate_files_logs_event(tmp_path, monkeypatch):
    workspace = tmp_path
    db_dir = workspace / "databases"
    doc_dir = workspace / "documentation"
    db_dir.mkdir()
    doc_dir.mkdir()
    doc_db = db_dir / "documentation.db"
    with sqlite3.connect(doc_db) as conn:
        conn.execute(
            "CREATE TABLE enterprise_documentation (doc_id TEXT, doc_type TEXT, content TEXT, source_path TEXT)"
        )
        conn.execute("INSERT INTO enterprise_documentation VALUES ('1','README','alpha','src/1.py')")

    analytics_db, completion_db = create_template_dbs(tmp_path)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("DOCUMENTATION_DB_PATH", str(doc_db))
    monkeypatch.setattr(TemplateAutoGenerator, "select_best_template", lambda *a, **k: "{content}")
    monkeypatch.setattr(EnterpriseDocumentationManager, "calculate_compliance", lambda *a, **k: 100.0)
    manager = EnterpriseDocumentationManager(
        workspace=workspace,
        db_path=doc_db,
        analytics_db=analytics_db,
        completion_db=completion_db,
    )
    manager.generate_files("README", output_formats=("md", "html", "pdf"))
    with sqlite3.connect(analytics_db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM correction_logs").fetchone()[0]
    assert count == 1


def test_cross_links_recorded_and_embedded(tmp_path, monkeypatch):
    workspace = tmp_path
    db_dir = workspace / "databases"
    doc_dir = workspace / "documentation"
    db_dir.mkdir()
    doc_dir.mkdir()
    doc_db = db_dir / "documentation.db"
    with sqlite3.connect(doc_db) as conn:
        conn.execute(
            "CREATE TABLE enterprise_documentation (doc_id TEXT, doc_type TEXT, content TEXT, source_path TEXT)"
        )
        conn.executemany(
            "INSERT INTO enterprise_documentation VALUES (?,?,?,?)",
            [("1", "README", "alpha", "src/1.py")],
        )

    analytics_db, completion_db = create_template_dbs(tmp_path)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("DOCUMENTATION_DB_PATH", str(doc_db))
    monkeypatch.setattr(TemplateAutoGenerator, "select_best_template", lambda *a, **k: "{content}")
    monkeypatch.setattr(EnterpriseDocumentationManager, "calculate_compliance", lambda *a, **k: 100.0)
    manager = EnterpriseDocumentationManager(
        workspace=workspace,
        db_path=doc_db,
        analytics_db=analytics_db,
        completion_db=completion_db,
    )

    manager.generate_files("README", output_formats=("md", "html", "pdf"))

    with sqlite3.connect(analytics_db) as conn:
        links = conn.execute("SELECT COUNT(*) FROM cross_link_events").fetchone()[0]
    assert links == 6
    md_file = workspace / "documentation" / "generated" / "enterprise_docs" / "1.md"
    text = md_file.read_text()
    assert "analytics://correction_logs/1" in text
    assert "analytics://audit_log/1" in text
