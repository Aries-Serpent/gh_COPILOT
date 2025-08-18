import os
import sqlite3
from pathlib import Path

os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"

from template_engine import workflow_enhancer
from template_engine.workflow_enhancer import TemplateWorkflowEnhancer


def _setup_db(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            "CREATE TABLE templates (template_name TEXT, template_content TEXT, compliance_score REAL, feature_vector TEXT)"
        )
        conn.execute("INSERT INTO templates VALUES ('A', 'alpha content', 0.8, '1,0')")
        conn.execute("INSERT INTO templates VALUES ('B', 'beta content', 0.6, '0,1')")


def test_dry_run_produces_no_artifacts_or_logs(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setattr(workflow_enhancer, "validate_enterprise_operation", lambda *_a, **_k: True)
    monkeypatch.setattr(workflow_enhancer, "collect_metrics", lambda: {"cpu_percent": 0.0})
    monkeypatch.setattr(
        workflow_enhancer, "DEFAULT_ANALYTICS_DB", tmp_path / "databases" / "analytics.db", raising=False
    )
    class DummyUpdater:
        def __init__(self, *_, **__):
            pass

        def _fetch_compliance_metrics(self, test_mode: bool = False):
            return {}

        def _cognitive_compliance_suggestion(self, metrics):
            return ""

        def _update_dashboard(self, metrics):
            return None

    monkeypatch.setattr(workflow_enhancer, "ComplianceMetricsUpdater", DummyUpdater)
    db = tmp_path / "prod.db"
    _setup_db(db)
    dashboard = tmp_path / "dash"
    enhancer = TemplateWorkflowEnhancer(db, dashboard, dry_run=True)
    enhancer.enhance(timeout_minutes=1)
    assert not list(dashboard.glob("workflow_enhancement_report_*.json"))
    analytics_db = tmp_path / "databases" / "analytics.db"
    count = 0
    if analytics_db.exists():
        with sqlite3.connect(analytics_db) as conn:
            table_exists = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='workflow_events'"
            ).fetchone()
            if table_exists:
                count = conn.execute("SELECT COUNT(*) FROM workflow_events").fetchone()[0]
    assert count == 0


def test_repeated_runs_do_not_duplicate(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setattr(workflow_enhancer, "validate_enterprise_operation", lambda *_a, **_k: True)
    monkeypatch.setattr(workflow_enhancer, "collect_metrics", lambda: {"cpu_percent": 0.0})
    monkeypatch.setattr(
        workflow_enhancer, "DEFAULT_ANALYTICS_DB", tmp_path / "databases" / "analytics.db", raising=False
    )
    class DummyUpdater:
        def __init__(self, *_, **__):
            pass

        def _fetch_compliance_metrics(self, test_mode: bool = False):
            return {}

        def _cognitive_compliance_suggestion(self, metrics):
            return ""

        def _update_dashboard(self, metrics):
            return None

    monkeypatch.setattr(workflow_enhancer, "ComplianceMetricsUpdater", DummyUpdater)
    db = tmp_path / "prod.db"
    _setup_db(db)
    dashboard = tmp_path / "dash"
    analytics_db = tmp_path / "databases" / "analytics.db"
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS workflow_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event TEXT,
                level TEXT,
                module TEXT,
                template_count INTEGER,
                cluster_count INTEGER,
                avg_score REAL,
                hash TEXT,
                duration REAL,
                timestamp TEXT
            )
            """
        )
    enhancer = TemplateWorkflowEnhancer(db, dashboard)
    enhancer.enhance(timeout_minutes=1)
    enhancer.enhance(timeout_minutes=1)
    files = list(dashboard.glob("workflow_enhancement_report_*.json"))
    assert len(files) == 1
    with sqlite3.connect(tmp_path / "databases" / "analytics.db") as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM workflow_events WHERE event='workflow_enhancement_report_generated'"
        ).fetchone()[0]
    assert count == 1
