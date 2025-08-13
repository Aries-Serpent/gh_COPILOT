import sqlite3
from typer.testing import CliRunner

from gh_copilot.cli import app

import scripts.database.documentation_ingestor as di
import scripts.database.template_asset_ingestor as ti
import scripts.generate_docs_metrics as gdm
import scripts.database.har_ingestor as hi


runner = CliRunner()


def _stub_validator():
    class _V:
        def validate_corrections(self, files):
            return True
    return _V()


class _DummyTqdm:
    def __init__(self, iterable=None, **k):
        self.iterable = iterable or range(k.get("total", 0))

    def __iter__(self):
        return iter(self.iterable)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def update(self, *a, **k):
        pass


def test_ingest_docs_cli(tmp_path, monkeypatch):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (tmp_path / "databases").mkdir()
    (docs_dir / "a.md").write_text("# A")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))

    monkeypatch.setattr(di, "enforce_anti_recursion", lambda *a, **k: None)
    monkeypatch.setattr(di, "validate_enterprise_operation", lambda *a, **k: None)
    monkeypatch.setattr(di, "get_dataset_sources", lambda *a, **k: [])
    monkeypatch.setattr(di, "log_sync_operation", lambda *a, **k: None)
    monkeypatch.setattr(di, "log_event", lambda *a, **k: None)
    monkeypatch.setattr(di, "SecondaryCopilotValidator", _stub_validator)
    monkeypatch.setattr(di, "tqdm", _DummyTqdm)

    result = runner.invoke(
        app,
        ["ingest-docs", "--workspace", str(tmp_path), "--docs-dir", str(docs_dir)],
    )
    assert result.exit_code == 0
    assert "\"ingested\": 1" in result.stdout


def test_ingest_templates_cli(tmp_path, monkeypatch):
    tmpl_dir = tmp_path / "templates"
    tmpl_dir.mkdir()
    (tmp_path / "databases").mkdir(exist_ok=True)
    (tmpl_dir / "t.md").write_text("# T")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))

    monkeypatch.setattr(ti, "validate_enterprise_operation", lambda *a, **k: None)
    monkeypatch.setattr(ti, "get_dataset_sources", lambda *a, **k: [])
    monkeypatch.setattr(ti, "get_lesson_templates", lambda *a, **k: {})
    monkeypatch.setattr(ti, "log_sync_operation", lambda *a, **k: None)
    monkeypatch.setattr(ti, "log_event", lambda *a, **k: None)
    monkeypatch.setattr(ti, "check_database_sizes", lambda *a, **k: True)
    monkeypatch.setattr(ti, "DualCopilotOrchestrator", lambda: type("O", (), {"validator": _stub_validator()})())
    monkeypatch.setattr(ti, "tqdm", _DummyTqdm)

    result = runner.invoke(
        app,
        [
            "ingest-templates",
            "--workspace",
            str(tmp_path),
            "--templates-dir",
            str(tmpl_dir),
        ],
    )
    assert result.exit_code == 0
    assert "\"ingested\": 1" in result.stdout


def test_ingest_har_cli(tmp_path, monkeypatch):
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    (tmp_path / "databases").mkdir(exist_ok=True)
    (logs_dir / "a.har").write_text("{}")
    (logs_dir / "b.har").write_text("{}")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))

    monkeypatch.setattr(hi, "validate_enterprise_operation", lambda *a, **k: None)
    monkeypatch.setattr(hi, "enforce_anti_recursion", lambda *a, **k: None)
    monkeypatch.setattr(hi, "log_sync_operation", lambda *a, **k: None)
    monkeypatch.setattr(hi, "log_event", lambda *a, **k: None)
    monkeypatch.setattr(hi, "check_database_sizes", lambda *a, **k: True)
    monkeypatch.setattr(hi, "SecondaryCopilotValidator", _stub_validator)
    monkeypatch.setattr(hi, "tqdm", _DummyTqdm)

    result = runner.invoke(
        app, ["ingest-har", "--workspace", str(tmp_path), "--har-dir", str(logs_dir)]
    )
    assert result.exit_code == 0
    assert "\"ingested\": 1" in result.stdout


def test_generate_docs_cli(tmp_path, monkeypatch):
    db_path = tmp_path / "prod.db"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE enterprise_script_tracking (id INTEGER)")
    conn.execute("INSERT INTO enterprise_script_tracking(id) VALUES (1)")
    conn.execute("CREATE TABLE script_template_patterns (id INTEGER)")
    conn.execute("INSERT INTO script_template_patterns(id) VALUES (1)")
    conn.commit()
    conn.close()

    readme = tmp_path / "README.md"
    readme.write_text("Generated on 2020-01-01 00:00:00\n")
    db_list = tmp_path / "DATABASE_LIST.md"
    db_list.write_text("- a.db\n- b.db\n")

    monkeypatch.setattr(gdm, "README_PATHS", [readme])
    monkeypatch.setattr(gdm, "DATABASE_LIST", db_list)
    monkeypatch.setattr(gdm, "_log_event", lambda *a, **k: None)
    monkeypatch.setattr(gdm, "SecondaryCopilotValidator", _stub_validator)
    monkeypatch.setattr(gdm, "run_dual_copilot_validation", lambda p, s: (p(), s()))
    monkeypatch.setattr(gdm.validate_docs_metrics, "validate", lambda path: True)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))

    result = runner.invoke(
        app,
        [
            "generate-docs",
            "--db-path",
            str(db_path),
            "--analytics-db",
            str(tmp_path / "analytics.db"),
        ],
    )
    assert result.exit_code == 0
    assert "\"scripts\": 1" in result.stdout
