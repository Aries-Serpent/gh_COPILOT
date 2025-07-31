import sqlite3
from documentation import EnterpriseDocumentationManager


def setup_db(doc_db):
    with sqlite3.connect(doc_db) as conn:
        conn.execute("CREATE TABLE documentation_templates (template_name TEXT, template_content TEXT, doc_type TEXT)")
        conn.execute("INSERT INTO documentation_templates VALUES ('default', 'Hello {count}', 'README')")
        conn.execute(
            "CREATE TABLE enterprise_documentation (doc_id INTEGER PRIMARY KEY AUTOINCREMENT, doc_type TEXT, title TEXT, content TEXT, compliance REAL)"
        )


def test_basic_generation(tmp_path, monkeypatch):
    doc_db = tmp_path / "docs.db"
    analytics = tmp_path / "analytics.db"
    setup_db(doc_db)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    manager = EnterpriseDocumentationManager(str(doc_db))
    templates = manager.discover_templates("README")
    assert templates == [("default", "Hello {count}")]
    content = manager.apply_template_intelligence(templates, [])
    score = manager.calculate_compliance(content)
    manager.store_documentation(content, score)
    with sqlite3.connect(analytics) as conn:
        count = conn.execute("SELECT COUNT(*) FROM documentation_events").fetchone()[0]
        assert count == 1
