import os
import sqlite3

import scripts.code_placeholder_audit as audit
from secondary_copilot_validator import SecondaryCopilotValidator


def test_auto_fill_integration(tmp_path, monkeypatch):
    os.environ["GH_COPILOT_WORKSPACE"] = str(tmp_path)
    prod = tmp_path / "production.db"
    analytics = tmp_path / "analytics.db"
    with sqlite3.connect(prod) as conn:
        conn.execute("CREATE TABLE template_placeholders (placeholder_name TEXT)")
    with sqlite3.connect(analytics) as conn:
        conn.execute(
            "CREATE TABLE todo_fixme_tracking (file_path TEXT, line_number INTEGER, placeholder_type TEXT, context TEXT, timestamp TEXT, resolved INTEGER, resolved_timestamp TEXT, status TEXT, removal_id INTEGER)"
        )
    test_file = tmp_path / "demo.py"
    test_file.write_text("x = 1  # TODO remove\n", encoding="utf-8")

    called = {}

    class StubUtility:
        def __init__(self, workspace_path="."):
            pass

        def perform_utility_function(self):
            gen_dir = tmp_path / "generated_templates"
            gen_dir.mkdir()
            (gen_dir / "template_stub.txt").write_text("filled content", encoding="utf-8")
            called["utility"] = True
            return True

    monkeypatch.setattr(audit, "EnterpriseUtility", StubUtility)
    monkeypatch.setattr(SecondaryCopilotValidator, "validate_corrections", lambda self, files: True)
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path.parent / "backups"))

    results = [{"file": str(test_file), "line": 1, "context": "", "pattern": "TODO"}]
    audit.auto_remove_placeholders(results, prod, analytics)

    assert called.get("utility") is True
    assert "filled content" in test_file.read_text(encoding="utf-8")

