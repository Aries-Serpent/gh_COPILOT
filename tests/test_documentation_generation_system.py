import sqlite3
from scripts.documentation_generation_system import EnterpriseUtility


def test_generation_system(tmp_path, monkeypatch):
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    db_path = db_dir / "documentation.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE documentation_templates (template_name TEXT, template_content TEXT, enterprise_compliant BOOLEAN)"
        )
        conn.execute(
            "INSERT INTO documentation_templates VALUES ('sample', '# Example', 1)"
        )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    util = EnterpriseUtility()
    assert util.perform_utility_function() is True
    output = tmp_path / "documentation" / "generated" / "templates" / "sample.md"
    assert output.exists()
    assert output.read_text() == "# Example"
