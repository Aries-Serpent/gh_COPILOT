import sqlite3

from scripts.intelligent_code_analysis_placeholder_detection import EnterpriseUtility


def test_placeholder_logging(tmp_path):
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    target = scripts_dir / "comprehensive_production_deployer.py"
    target.write_text("def demo():\n    pass  # TODO")

    db_path = tmp_path / "analytics.db"
    util = EnterpriseUtility(workspace_path=str(tmp_path), db_path=str(db_path))
    assert not util.perform_utility_function()

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT file_path, pattern, severity FROM placeholder_audit"
        ).fetchone()
    assert row[0].endswith("comprehensive_production_deployer.py")
    assert row[1] == "TODO"
    assert row[2] == "low"

