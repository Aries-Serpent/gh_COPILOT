import sqlite3



def test_placeholder_cleanup_workflow(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    from scripts import code_placeholder_audit as audit
    monkeypatch.setattr(
        "scripts.code_placeholder_audit.SecondaryCopilotValidator.validate_corrections",
        lambda self, files: True,
    )
    monkeypatch.setattr(
        "scripts.correction_logger_and_rollback.validate_enterprise_operation",
        lambda: None,
    )
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
    audit.main(
        workspace_path=str(workspace),
        analytics_db=str(analytics),
        production_db=str(prod),
        dashboard_dir=str(dash),
        apply_fixes=True,
    )

    cleaned = target.read_text()
    assert "TODO" not in cleaned
    assert "{{OLD}}" not in cleaned
    with sqlite3.connect(analytics) as conn:
        count = conn.execute("SELECT COUNT(*) FROM corrections").fetchone()[0]
    assert count >= 1
    summary = dash / "compliance" / "placeholder_summary.json"
    if summary.exists():
        assert summary.read_text()
