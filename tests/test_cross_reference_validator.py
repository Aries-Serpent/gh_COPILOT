import importlib
import json
import sqlite3
from pathlib import Path


def test_cross_reference_validator_updates_dashboard(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))

    crv = importlib.import_module("scripts.cross_reference_validator")
    importlib.reload(crv)
    monkeypatch.setattr(crv, "validate_enterprise_operation", lambda *a, **k: True)

    production_db = tmp_path / "production.db"
    with sqlite3.connect(production_db) as conn:
        conn.execute("CREATE TABLE cross_reference_patterns (pattern_name TEXT)")
        conn.execute("CREATE TABLE code_templates (id INTEGER PRIMARY KEY, template_code TEXT)")
        conn.execute("INSERT INTO code_templates VALUES (1, 'foo template')")
        conn.execute("INSERT INTO cross_reference_patterns VALUES ('foo')")

    analytics_db = tmp_path / "databases" / "analytics.db"
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """
            CREATE TABLE todo_fixme_tracking (
                file_path TEXT,
                item_type TEXT,
                status TEXT,
                last_updated TEXT
            )
            """
        )
        conn.execute("INSERT INTO todo_fixme_tracking VALUES ('file.py', 'code', 'open', '2024-01-01')")
        conn.execute(
            """
            CREATE TABLE cross_link_events (
                file_path TEXT NOT NULL,
                linked_path TEXT NOT NULL,
                timestamp TEXT,
                module TEXT,
                level TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE cross_link_summary (
                actions INTEGER,
                links INTEGER,
                summary_path TEXT,
                timestamp TEXT,
                module TEXT,
                level TEXT
            )
            """
        )

    dashboard_dir = tmp_path / "dashboard"
    task_file = tmp_path / "tasks.md"
    task_file.write_text("- [ ] Example task\n", encoding="utf-8")

    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "file.py").write_text("docs")
    code_dir = tmp_path / "copilot"
    code_dir.mkdir()
    (code_dir / "file.py").write_text("code")

    validator = crv.CrossReferenceValidator(production_db, analytics_db, dashboard_dir, task_file)
    assert validator.validate(timeout_minutes=1)

    summary_file = dashboard_dir / "cross_reference_summary.json"
    assert summary_file.exists()
    data = json.loads(summary_file.read_text())
    assert len(data["cross_linked_actions"]) == 1
    assert "recommended_links" in data
    assert data["recommended_links"]

    with sqlite3.connect(analytics_db) as conn:
        rows = conn.execute(
            "SELECT file_path, linked_path FROM cross_link_events"
        ).fetchall()
        summary = conn.execute(
            "SELECT actions, links, summary_path FROM cross_link_summary"
        ).fetchall()

    assert len(rows) == 2
    assert {Path(r[1]).name for r in rows} == {"file.py"}
    assert len(summary) == 1
    actions, links, path = summary[0]
    assert actions == 1
    assert links == len(rows)
    assert Path(path) == summary_file


def test_deep_cross_link_excludes_backup(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    backup_root = tmp_path / "backups"
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))

    crv = importlib.import_module("scripts.cross_reference_validator")
    importlib.reload(crv)
    monkeypatch.setattr(crv, "validate_enterprise_operation", lambda *a, **k: True)

    production_db = tmp_path / "production.db"
    with sqlite3.connect(production_db) as conn:
        conn.execute("CREATE TABLE cross_reference_patterns (pattern_name TEXT)")

    analytics_db = tmp_path / "databases" / "analytics.db"
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """
            CREATE TABLE todo_fixme_tracking (
                file_path TEXT,
                item_type TEXT,
                status TEXT,
                last_updated TEXT
            )
            """
        )
        conn.execute("INSERT INTO todo_fixme_tracking VALUES ('target.py', 'code', 'open', '2024-01-01')")
        conn.execute(
            """
            CREATE TABLE cross_link_events (
                file_path TEXT NOT NULL,
                linked_path TEXT NOT NULL,
                timestamp TEXT,
                module TEXT,
                level TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE cross_link_summary (
                actions INTEGER,
                links INTEGER,
                summary_path TEXT,
                timestamp TEXT,
                module TEXT,
                level TEXT
            )
            """
        )

    dashboard_dir = tmp_path / "dashboard"
    task_file = tmp_path / "tasks.md"
    task_file.write_text("- [ ] Example task\n", encoding="utf-8")

    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "target.py").write_text("docs")
    code_dir = tmp_path / "copilot"
    code_dir.mkdir()
    (code_dir / "target.py").write_text("code")
    backup_root.mkdir()
    (backup_root / "target.py").write_text("backup")

    validator = crv.CrossReferenceValidator(production_db, analytics_db, dashboard_dir, task_file)
    assert validator.validate(timeout_minutes=1)

    with sqlite3.connect(analytics_db) as conn:
        paths = {Path(row[0]) for row in conn.execute("SELECT linked_path FROM cross_link_events")}

    assert (docs_dir / "target.py") in paths
    assert (code_dir / "target.py") in paths
    assert (backup_root / "target.py") not in paths

    assert all(Path(entry["linked_path"]) != backup_root / "target.py" for entry in validator.cross_link_log)


def test_deep_cross_link_respects_updated_backup_env(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    first_backup = tmp_path / "backup1"
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(first_backup))

    crv = importlib.import_module("scripts.cross_reference_validator")
    importlib.reload(crv)
    monkeypatch.setattr(crv, "validate_enterprise_operation", lambda *a, **k: True)

    production_db = tmp_path / "production.db"
    with sqlite3.connect(production_db) as conn:
        conn.execute("CREATE TABLE cross_reference_patterns (pattern_name TEXT)")

    analytics_db = tmp_path / "databases" / "analytics.db"
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """
            CREATE TABLE todo_fixme_tracking (
                file_path TEXT,
                item_type TEXT,
                status TEXT,
                last_updated TEXT
            )
            """
        )
        conn.execute(
            "INSERT INTO todo_fixme_tracking VALUES ('target.py', 'code', 'open', '2024-01-01')"
        )
        conn.execute(
            """
            CREATE TABLE cross_link_events (
                file_path TEXT NOT NULL,
                linked_path TEXT NOT NULL,
                timestamp TEXT,
                module TEXT,
                level TEXT
            )
            """
        )

    dashboard_dir = tmp_path / "dashboard"
    task_file = tmp_path / "tasks.md"
    task_file.write_text("- [ ] Example task\n", encoding="utf-8")

    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "target.py").write_text("docs")
    code_dir = tmp_path / "copilot"
    code_dir.mkdir()
    (code_dir / "target.py").write_text("code")
    validator = crv.CrossReferenceValidator(
        production_db, analytics_db, dashboard_dir, task_file
    )

    second_backup = tmp_path / "backup2"
    second_backup.mkdir()
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(second_backup))
    (second_backup / "target.py").write_text("backup2")

    assert validator.validate(timeout_minutes=1)

    with sqlite3.connect(analytics_db) as conn:
        paths = {Path(row[0]) for row in conn.execute("SELECT linked_path FROM cross_link_events")}

    assert (docs_dir / "target.py") in paths
    assert (code_dir / "target.py") in paths
    assert (second_backup / "target.py") not in paths

    assert all(
        Path(entry["linked_path"]) != second_backup / "target.py"
        for entry in validator.cross_link_log
    )


def test_suggest_links_logged(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))

    crv = importlib.import_module("scripts.cross_reference_validator")
    importlib.reload(crv)
    monkeypatch.setattr(crv, "validate_enterprise_operation", lambda *a, **k: True)

    production_db = tmp_path / "production.db"
    with sqlite3.connect(production_db) as conn:
        conn.execute("CREATE TABLE cross_reference_patterns (pattern_name TEXT)")

    analytics_db = tmp_path / "databases" / "analytics.db"
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """
            CREATE TABLE todo_fixme_tracking (
                file_path TEXT,
                item_type TEXT,
                status TEXT,
                last_updated TEXT
            )
            """
        )
        conn.execute("INSERT INTO todo_fixme_tracking VALUES ('feature_new.py', 'code', 'open', '2024-01-01')")
        conn.execute(
            "INSERT INTO cross_link_events VALUES ('feature_old.py', 'docs/feature_old.md', '2024-01-01', 'test', 'INFO')"
        )
        conn.execute(
            """
            CREATE TABLE cross_link_suggestions (
                file_path TEXT NOT NULL,
                suggested_link TEXT NOT NULL,
                score REAL,
                timestamp TEXT,
                module TEXT,
                level TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE cross_link_summary (
                actions INTEGER,
                links INTEGER,
                summary_path TEXT,
                timestamp TEXT,
                module TEXT,
                level TEXT
            )
            """
        )
        conn.execute("INSERT INTO cross_link_events VALUES ('feature_old.py', 'docs/feature_old.md', '2024-01-01')")

    dashboard_dir = tmp_path / "dashboard"
    task_file = tmp_path / "tasks.md"
    task_file.write_text("- [ ] Example task\n", encoding="utf-8")

    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "feature_new.py").write_text("docs")
    code_dir = tmp_path / "copilot"
    code_dir.mkdir()
    (code_dir / "feature_new.py").write_text("code")

    validator = crv.CrossReferenceValidator(production_db, analytics_db, dashboard_dir, task_file)
    assert validator.validate(timeout_minutes=1)

    summary = json.loads((dashboard_dir / "cross_reference_summary.json").read_text())
    assert summary["suggested_links"]
    assert summary["recommended_links"] == []

    with sqlite3.connect(analytics_db) as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        count = conn.execute("SELECT COUNT(*) FROM cross_link_suggestions").fetchone()[0]
        rec_count = conn.execute("SELECT COUNT(*) FROM cross_link_recommendations").fetchone()[0]

    assert "cross_link_suggestions" in tables
    assert "cross_link_recommendations" in tables
    assert count >= 1
    assert rec_count == 0


def test_cross_reference_validator_timeout(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))

    crv = importlib.import_module("scripts.cross_reference_validator")
    importlib.reload(crv)
    monkeypatch.setattr(crv, "validate_enterprise_operation", lambda *a, **k: True)

    production_db = tmp_path / "production.db"
    with sqlite3.connect(production_db) as conn:
        conn.execute("CREATE TABLE cross_reference_patterns (pattern_name TEXT)")
        conn.execute("INSERT INTO cross_reference_patterns VALUES ('foo')")

    analytics_db = tmp_path / "analytics.db"
    with sqlite3.connect(analytics_db) as conn:
        conn.execute("CREATE TABLE cross_link_events (file_path TEXT, linked_path TEXT, timestamp TEXT)")

    dashboard_dir = tmp_path / "dashboard"
    task_file = tmp_path / "tasks.md"
    task_file.write_text("- [ ] Example task\n", encoding="utf-8")

    logged: list[dict] = []
    monkeypatch.setattr(crv, "_log_event", lambda event, **_: logged.append(event))

    validator = crv.CrossReferenceValidator(production_db, analytics_db, dashboard_dir, task_file)

    times = iter([0, 61])
    monkeypatch.setattr(crv.time, "time", lambda: next(times))

    assert not validator.validate(timeout_minutes=1)
    assert logged and logged[-1]["event"] == "cross_reference_timeout"
