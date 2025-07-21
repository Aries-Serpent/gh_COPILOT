import sqlite3
from documentation.enterprise_documentation_manager import EnterpriseDocumentationManager


def setup_db(doc_db):
    with sqlite3.connect(doc_db) as conn:
        conn.execute(
            "CREATE TABLE documentation_templates (doc_type TEXT, template_content TEXT)"
        )
        conn.execute(
            "INSERT INTO documentation_templates VALUES ('README', 'Hello {count}')"
        )
        conn.execute(
            "CREATE TABLE enterprise_documentation (doc_id INTEGER PRIMARY KEY AUTOINCREMENT, doc_type TEXT, title TEXT, content TEXT, compliance REAL)"
        )


def test_basic_generation(tmp_path):
    doc_db = tmp_path / "docs.db"
    analytics = tmp_path / "analytics.db"
    setup_db(doc_db)
    manager = EnterpriseDocumentationManager(doc_db, analytics)
    templates = manager.discover_templates("README")
    assert templates == ["Hello {count}"]
    content = manager.apply_template_intelligence(templates, [])
    score = manager.calculate_compliance(content)
    manager.store_documentation(content, score)
    with sqlite3.connect(doc_db) as conn:
        row = conn.execute("SELECT content, compliance FROM enterprise_documentation").fetchone()
        assert row == (content, score)
    with sqlite3.connect(analytics) as conn:
        count = conn.execute("SELECT COUNT(*) FROM generation_events").fetchone()[0]
        assert count == 1
