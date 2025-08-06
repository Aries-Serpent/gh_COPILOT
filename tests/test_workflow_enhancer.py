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


def test_workflow_enhancer_basic(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setattr(workflow_enhancer, "validate_enterprise_operation", lambda *_a, **_k: True)
    db = tmp_path / "prod.db"
    _setup_db(db)
    dashboard = tmp_path / "dash"
    enhancer = TemplateWorkflowEnhancer(db, dashboard)
    templates = enhancer.fetch_templates()
    assert len(templates) == 2
    clusters = enhancer.cluster_templates(templates, n_clusters=2)
    assert len(clusters) == 2
    score = enhancer.score_compliance(templates)
    assert score > 0


def test_pattern_mining(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setattr(workflow_enhancer, "validate_enterprise_operation", lambda *_a, **_k: True)
    db = tmp_path / "prod.db"
    _setup_db(db)
    dashboard = tmp_path / "dash"
    enhancer = TemplateWorkflowEnhancer(db, dashboard)
    templates = enhancer.fetch_templates()
    patterns = enhancer.mine_patterns(templates)
    assert "content" in patterns


def test_cluster_templates_handles_missing_features(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setattr(workflow_enhancer, "validate_enterprise_operation", lambda *_a, **_k: True)
    db = tmp_path / "prod.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE templates (template_name TEXT, template_content TEXT, compliance_score REAL, feature_vector TEXT)"
        )
        conn.execute("INSERT INTO templates VALUES ('A', 'alpha', 0.9, '1,0')")
        conn.execute("INSERT INTO templates VALUES ('B', 'beta', 0.8, '')")
    dashboard = tmp_path / "dash"
    enhancer = TemplateWorkflowEnhancer(db, dashboard)
    templates = enhancer.fetch_templates()
    clusters = enhancer.cluster_templates(templates, n_clusters=2)
    total = sum(len(v) for v in clusters.values())
    assert total == 1


def test_generate_compliance_report(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setattr(workflow_enhancer, "validate_enterprise_operation", lambda *_a, **_k: True)
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
    enhancer = TemplateWorkflowEnhancer(db, dashboard)
    templates = enhancer.fetch_templates()
    report = enhancer.generate_compliance_report(templates)
    assert report["total_templates"] == 2
    assert report["cluster_count"] >= 1
    assert "average_compliance_score" in report
    assert "recommendations" in report


def test_enhancement_respects_monitoring(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setattr(workflow_enhancer, "validate_enterprise_operation", lambda *_a, **_k: True)
    monkeypatch.setattr(
        workflow_enhancer,
        "collect_metrics",
        lambda: {"cpu_percent": 95.0},
    )
    monkeypatch.setattr(
        workflow_enhancer,
        "DEFAULT_ANALYTICS_DB",
        tmp_path / "analytics.db",
        raising=False,
    )
    db = tmp_path / "prod.db"
    _setup_db(db)
    dashboard = tmp_path / "dash"
    enhancer = TemplateWorkflowEnhancer(db, dashboard)
    assert not enhancer.enhance(timeout_minutes=1)
    assert not (dashboard / "workflow_enhancement_report.json").exists()
