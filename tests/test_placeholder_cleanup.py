import os
import sqlite3
from pathlib import Path

import scripts.placeholder_cleanup as pc


def test_placeholder_cleanup_workflow(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    workspace = tmp_path / "ws"
    workspace.mkdir()
    target = workspace / "demo.py"
    target.write_text("def demo():\n    pass  # TODO\n    print('{{OLD}}')\n")

    prod = tmp_path / "production.db"
    analytics = tmp_path / "analytics.db"
    dash = tmp_path / "dashboard"
    with sqlite3.connect(prod) as conn:
        conn.execute("CREATE TABLE template_placeholders (placeholder_name TEXT)")
        conn.execute("INSERT INTO template_placeholders VALUES ('VALID')")
    pc.main(workspace, analytics, prod, dash)

    cleaned = target.read_text()
    assert "TODO" not in cleaned
    assert "{{OLD}}" not in cleaned
    with sqlite3.connect(analytics) as conn:
        count = conn.execute("SELECT COUNT(*) FROM corrections").fetchone()[0]
    assert count >= 1
    metrics = (dash / "metrics.json").read_text()
    assert metrics
