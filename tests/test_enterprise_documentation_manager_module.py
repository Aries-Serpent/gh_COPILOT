import logging
import sqlite3
from documentation.enterprise_documentation_manager import EnterpriseDocumentationManager


def test_documentation_generation(tmp_path, monkeypatch, caplog):
    db_path = tmp_path / "docs.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE enterprise_documentation (doc_id TEXT, doc_type TEXT, title TEXT, content TEXT)"
        )
        conn.execute(
            "CREATE TABLE documentation_templates (template_name TEXT, template_content TEXT, doc_type TEXT)"
        )
        conn.execute(
            "INSERT INTO documentation_templates VALUES ('t1', '# Title {count}', 'README')"
        )
        conn.execute(
            "INSERT INTO enterprise_documentation VALUES ('1', 'README', 'Title1', 'old')"
        )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    mgr = EnterpriseDocumentationManager(db_path=str(db_path))
    with caplog.at_level(logging.INFO):
        existing = mgr.query_documentation_database("README")
        templates = mgr.discover_templates("README")
        tpl = mgr.select_optimal_template(templates, existing)
        content = mgr.apply_template_intelligence([tpl], existing)
        score = mgr.calculate_compliance(content)
        mgr.store_documentation(content, score)
    assert "Compliance score" in " ".join(caplog.messages)
    with sqlite3.connect(tmp_path / "analytics.db") as conn:
        rows = conn.execute("SELECT COUNT(*) FROM documentation_events").fetchone()[0]
        assert rows == 1
