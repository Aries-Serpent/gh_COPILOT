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


def test_record_unresolved_placeholders_ignores_duplicates(tmp_path):
    analytics = tmp_path / "analytics.db"
    rows = [
        {"file": "a.py", "line": 1, "pattern": "TODO", "context": "# TODO"},
        {"file": "a.py", "line": 1, "pattern": "TODO", "context": "# TODO again"},
    ]
    audit.record_unresolved_placeholders(rows, analytics)
    audit.record_unresolved_placeholders(rows, analytics)
    with sqlite3.connect(analytics) as conn:
        count = conn.execute("SELECT COUNT(*) FROM unresolved_placeholders").fetchone()[0]
    assert count == 1


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
        assert cur.fetchone()[0].strip() == "# remove"


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
    assert resolved == 2
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
    monkeypatch.setattr("scripts.database.add_violation_logs.ensure_violation_logs", lambda *a, **k: None)
    monkeypatch.setattr("enterprise_modules.compliance.ensure_violation_logs", lambda *a, **k: None)
    monkeypatch.setattr("scripts.correction_logger_and_rollback.ensure_violation_logs", lambda *a, **k: None)
    monkeypatch.setattr("scripts.database.add_rollback_logs.ensure_rollback_logs", lambda *a, **k: None)
    monkeypatch.setattr("enterprise_modules.compliance.ensure_rollback_logs", lambda *a, **k: None)
    monkeypatch.setattr("scripts.correction_logger_and_rollback.ensure_rollback_logs", lambda *a, **k: None)
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
        cur = conn.execute("SELECT status, resolved FROM todo_fixme_tracking")
        status, resolved = cur.fetchone()
    assert status == "resolved" and resolved == 1
    resolved_file = dashboard / "resolved_placeholders.json"
    assert resolved_file.exists()


def test_apply_suggestions_updates_file_and_db(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    src = workspace / "example.py"
    src.write_text("# FIXME: adjust\n", encoding="utf-8")
    prod_db, analytics_db = _prepare_dbs(tmp_path)
    dashboard = workspace / "dashboard" / "compliance"
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))
    audit.main(
        workspace_path=str(workspace),
        analytics_db=str(analytics_db),
        production_db=str(prod_db),
        dashboard_dir=str(dashboard),
        timeout_minutes=1,
        simulate=False,
        exclude_dirs=None,
        update_resolutions=False,
        apply_fixes=False,
        apply_suggestions=True,
        auto_resolve=False,
        export=None,
        task_report=None,
        summary_json=None,
        fail_on_findings=False,
    )
    assert "FIXME" not in src.read_text()
    with sqlite3.connect(analytics_db) as conn:
        unresolved = conn.execute("SELECT COUNT(*) FROM placeholder_tasks WHERE status='open'").fetchone()[0]
    assert unresolved == 0


def test_apply_suggestions_ignores_files_outside_workspace(tmp_path, capsys):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    outside = tmp_path / "outside.py"
    outside.write_text("# FIXME: adjust\n", encoding="utf-8")
    analytics_db = tmp_path / "analytics.db"
    tasks = [
        {
            "file": str(outside),
            "line": 1,
            "pattern": "FIXME",
            "context": "# FIXME: adjust",
            "suggestion": "# fixed",
        }
    ]
    unresolved = audit.apply_suggestions_to_files(tasks, analytics_db, workspace)
    out, _ = capsys.readouterr()
    assert unresolved == tasks
    assert outside.read_text(encoding="utf-8") == "# FIXME: adjust\n"
    assert "outside workspace" in out


def test_apply_suggestions_ignores_relative_paths_outside_workspace(tmp_path, capsys):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    outside = tmp_path / "outside.py"
    outside.write_text("# TODO: keep\n", encoding="utf-8")
    analytics_db = tmp_path / "analytics.db"
    tasks = [
        {
            "file": "../outside.py",
            "line": 1,
            "pattern": "TODO",
            "context": "# TODO: keep",
            "suggestion": "# done",
        }
    ]
    unresolved = audit.apply_suggestions_to_files(tasks, analytics_db, workspace)
    out, _ = capsys.readouterr()
    assert unresolved == tasks
    assert outside.read_text(encoding="utf-8") == "# TODO: keep\n"
    assert "outside workspace" in out


def test_apply_suggestions_skips_missing_tracking_entry(tmp_path):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    src = workspace / "foo.py"
    src.write_text("# TODO: fix\n", encoding="utf-8")
    analytics_db = tmp_path / "analytics.db"
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            "CREATE TABLE todo_fixme_tracking (file_path TEXT, line_number INTEGER, placeholder_type TEXT, context TEXT, suggestion TEXT, resolved INTEGER, resolved_timestamp TEXT, resolved_by TEXT, status TEXT)"
        )
        conn.commit()
    tasks = [
        {
            "file": str(src),
            "line": 1,
            "pattern": "TODO",
            "context": "# TODO: fix",
            "suggestion": "# done",
        }
    ]
    unresolved = audit.apply_suggestions_to_files(tasks, analytics_db, workspace)
    assert unresolved == tasks
    assert src.read_text(encoding="utf-8") == "# TODO: fix\n"
    with sqlite3.connect(analytics_db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM todo_fixme_tracking").fetchone()[0]
    assert count == 0


def test_placeholder_tasks_logged(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    src = workspace / "sample.py"
    src.write_text("# TODO: later\n", encoding="utf-8")
    prod_db, analytics_db = _prepare_dbs(tmp_path)
    dashboard = workspace / "dashboard" / "compliance"
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))
    audit.main(
        workspace_path=str(workspace),
        analytics_db=str(analytics_db),
        production_db=str(prod_db),
        dashboard_dir=str(dashboard),
        timeout_minutes=1,
        simulate=False,
        exclude_dirs=None,
        update_resolutions=False,
        apply_fixes=False,
        apply_suggestions=False,
        auto_resolve=False,
        export=None,
        task_report=None,
        summary_json=None,
        fail_on_findings=False,
    )
    with sqlite3.connect(analytics_db) as conn:
        row = conn.execute("SELECT file_path, line_number FROM placeholder_tasks").fetchone()
        metrics_rows = conn.execute("SELECT COUNT(*) FROM placeholder_metrics").fetchone()[0]
    assert row == (str(src), 1)
    # only one metrics row should exist per audit
    assert metrics_rows == 1
