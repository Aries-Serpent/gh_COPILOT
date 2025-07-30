import os
import sqlite3
from pathlib import Path

os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"

from scripts.code_placeholder_audit import main


def test_apply_fixes_removes_placeholders(tmp_path: Path) -> None:
    workspace = tmp_path / "ws"
    workspace.mkdir()
    target = workspace / "demo.py"
    target.write_text("def demo():\n    pass  # TODO\n")

    analytics = tmp_path / "analytics.db"
    prod_db = tmp_path / "production.db"
    with sqlite3.connect(prod_db) as conn:
        conn.execute(
            "CREATE TABLE template_placeholders (placeholder_name TEXT)"
        )
        conn.execute("INSERT INTO template_placeholders VALUES ('PLACE')")

    os.environ["GH_COPILOT_WORKSPACE"] = str(workspace)
    assert main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=str(prod_db),
        dashboard_dir=str(tmp_path / "dashboard"),
        apply_fixes=True,
    )

    assert "TODO" not in target.read_text()
    with sqlite3.connect(analytics) as conn:
        count = conn.execute("SELECT COUNT(*) FROM corrections").fetchone()[0]
    assert count >= 1
