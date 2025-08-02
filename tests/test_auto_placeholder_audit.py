import os
import sqlite3

from scripts.code_placeholder_audit import auto_remove_placeholders
from secondary_copilot_validator import SecondaryCopilotValidator


def test_auto_remove_triggers_validator(tmp_path, monkeypatch):
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

    called: dict[str, list[str]] = {}

    def fake_validate(self, files):
        called["files"] = files
        return True

    monkeypatch.setattr(SecondaryCopilotValidator, "validate_corrections", fake_validate)

    results = [{"file": str(test_file), "line": 1, "context": "", "pattern": "TODO"}]
    auto_remove_placeholders(results, prod, analytics)

    assert called.get("files") == [str(test_file)]

