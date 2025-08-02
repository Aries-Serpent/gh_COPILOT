import sqlite3
from template_engine.template_placeholder_remover import remove_unused_placeholders
from template_engine.db_first_code_generator import TemplateAutoGenerator, DBFirstCodeGenerator


def test_remove_unused_placeholders_logs_event(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    prod_db = tmp_path / "prod.db"
    analytics_db = tmp_path / "databases" / "analytics.db"
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS placeholder_removal_events (
                event TEXT,
                placeholder TEXT,
                removal_id INTEGER,
                removed INTEGER,
                timestamp TEXT,
                level TEXT,
                module TEXT
            )
            """
        )
        conn.commit()
    with sqlite3.connect(prod_db) as conn:
        conn.execute(
            "CREATE TABLE template_placeholders (placeholder_name TEXT, default_value TEXT)"
        )
        conn.commit()
    result = remove_unused_placeholders(
        "print('x') {{UNKNOWN}}",
        production_db=prod_db,
        analytics_db=analytics_db,
        timeout_minutes=1,
    )
    assert "{{UNKNOWN}}" not in result
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        ph = conn.execute(
            "SELECT placeholder FROM placeholder_removal_events"
        ).fetchone()[0]
        assert ph == "UNKNOWN"


def test_rank_templates_logs_and_strips(tmp_path):
    analytics_db = tmp_path / "databases" / "analytics.db"
    completion_db = tmp_path / "completion.db"
    prod_db = tmp_path / "prod.db"
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            "CREATE TABLE generator_events (event TEXT, target TEXT, template_id INTEGER, score REAL, count INTEGER, clusters INTEGER, items INTEGER, duration REAL, best_template TEXT, timestamp TEXT, level TEXT, module TEXT, candidates INTEGER, best_score REAL)"
        )
        conn.commit()
    gen = TemplateAutoGenerator(
        analytics_db=analytics_db, completion_db=completion_db, production_db=prod_db
    )
    gen.templates = ["print('{{PH}} b')", "print('b')"]
    ranked = gen.rank_templates("print('b')")
    assert ranked[0].strip() == "print('b')"
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        row = conn.execute(
            "SELECT event FROM generator_events WHERE event='rank_complete'"
        ).fetchone()
        assert row is not None


def test_generate_integration_ready_code_removes_placeholders(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_TEST_MODE", "1")
    analytics_db = workspace / "databases" / "analytics.db"
    production_db = workspace / "prod.db"
    documentation_db = workspace / "doc.db"
    template_db = workspace / "tmpl.db"
    with sqlite3.connect(production_db) as conn:
        conn.execute(
            "CREATE TABLE template_placeholders (placeholder_name TEXT, default_value TEXT)"
        )
        conn.commit()
    gen = DBFirstCodeGenerator(
        production_db=production_db,
        documentation_db=documentation_db,
        template_db=template_db,
        analytics_db=analytics_db,
    )
    gen.templates = ["print('hi')\n# {{UNKNOWN}}"]
    monkeypatch.setattr(
        "template_engine.db_first_code_generator.validate_no_recursive_folders",
        lambda: None,
    )
    monkeypatch.setattr(
        "template_engine.template_placeholder_remover.validate_no_recursive_folders",
        lambda: None,
    )
    (workspace / "logs" / "template_rendering").mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(workspace)
    path = gen.generate_integration_ready_code("demo")
    assert "{{UNKNOWN}}" not in path.read_text()
