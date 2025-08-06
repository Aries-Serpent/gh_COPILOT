import sqlite3
from pathlib import Path

import scripts.code_placeholder_audit as audit


def _prepare_dbs(tmp_path: Path):
    prod_db = tmp_path / "production.db"
    with sqlite3.connect(prod_db) as conn:
        conn.execute("CREATE TABLE template_placeholders (placeholder_name TEXT)")
        conn.commit()
    analytics_db = tmp_path / "analytics.db"
    return prod_db, analytics_db


def test_generate_fix_suggestions(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    file_path = workspace / "sample.py"
    file_path.write_text("# placeholder {{UNUSED}}\n", encoding="utf-8")
    prod_db, analytics_db = _prepare_dbs(tmp_path)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))
    results = [
        {
            "file": str(file_path),
            "line": 1,
            "pattern": "placeholder",
            "context": "# placeholder {{UNUSED}}",
        }
    ]
    tasks = audit.generate_removal_tasks(results, prod_db, analytics_db)
    assert tasks[0]["suggestion"].strip() == "# placeholder"


def test_suggestions_logged_to_tracking(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    src = workspace / "foo.py"
    src.write_text("# TODO: remove\n", encoding="utf-8")
    prod_db, analytics_db = _prepare_dbs(tmp_path)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    results = [
        {
            "file": str(src),
            "line": 1,
            "pattern": "TODO",
            "context": "# TODO: remove",
        }
    ]
    audit.log_findings(results, analytics_db)
    tasks = audit.generate_removal_tasks(results, prod_db, analytics_db)
    audit.log_placeholder_tasks(tasks, analytics_db)
    with sqlite3.connect(analytics_db) as conn:
        cur = conn.execute("SELECT suggestion FROM todo_fixme_tracking")
        assert "TODO" in cur.fetchone()[0]


def test_verify_task_completion_marks_resolved(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    src = workspace / "bar.py"
    src.write_text("# FIXME: issue\n", encoding="utf-8")
    prod_db, analytics_db = _prepare_dbs(tmp_path)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    results = [
        {
            "file": str(src),
            "line": 1,
            "pattern": "FIXME",
            "context": "# FIXME: issue",
        }
    ]
    audit.log_findings(results, analytics_db)
    tasks = audit.generate_removal_tasks(results, prod_db, analytics_db)
    audit.log_placeholder_tasks(tasks, analytics_db)
    # Simulate manual fix
    src.write_text("# done\n", encoding="utf-8")
    resolved = audit.verify_task_completion(analytics_db, workspace)
    assert resolved == 1
    with sqlite3.connect(analytics_db) as conn:
        cur = conn.execute("SELECT status, resolved FROM todo_fixme_tracking")
        status, resolved_flag = cur.fetchone()
    assert status == "resolved" and resolved_flag == 1


def test_apply_fixes_updates_db_and_file(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    src = workspace / "example.py"
    src.write_text("# TODO: remove\n", encoding="utf-8")
    prod_db, analytics_db = _prepare_dbs(tmp_path)
    dashboard = workspace / "dashboard" / "compliance"
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setattr(
        "scripts.database.add_violation_logs.ensure_violation_logs", lambda *a, **k: None
    )
    monkeypatch.setattr(
        "enterprise_modules.compliance.ensure_violation_logs", lambda *a, **k: None
    )
    monkeypatch.setattr(
        "scripts.correction_logger_and_rollback.ensure_violation_logs", lambda *a, **k: None
    )
    monkeypatch.setattr(
        "scripts.database.add_rollback_logs.ensure_rollback_logs", lambda *a, **k: None
    )
    monkeypatch.setattr(
        "enterprise_modules.compliance.ensure_rollback_logs", lambda *a, **k: None
    )
    monkeypatch.setattr(
        "scripts.correction_logger_and_rollback.ensure_rollback_logs", lambda *a, **k: None
    )
    audit.main(
        workspace_path=str(workspace),
        analytics_db=str(analytics_db),
        production_db=str(prod_db),
        dashboard_dir=str(dashboard),
        timeout_minutes=1,
        simulate=False,
        exclude_dirs=None,
        update_resolutions=False,
        apply_fixes=True,
        export=None,
        task_report=None,
        summary_json=None,
        fail_on_findings=False,
    )
    assert "TODO" not in src.read_text()
    with sqlite3.connect(analytics_db) as conn:
        cur = conn.execute(
            "SELECT status, resolved FROM todo_fixme_tracking"
        )
        status, resolved = cur.fetchone()
    assert status == "resolved" and resolved == 1
    resolved_file = dashboard / "resolved_placeholders.json"
    assert resolved_file.exists()
