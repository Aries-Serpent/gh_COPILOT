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
