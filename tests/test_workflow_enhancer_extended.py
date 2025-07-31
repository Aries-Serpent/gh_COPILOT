import json
import sqlite3
from pathlib import Path

from template_engine.workflow_enhancer import TemplateWorkflowEnhancer


def _create_db(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            "CREATE TABLE templates (template_name TEXT, template_content TEXT, compliance_score REAL, feature_vector TEXT)"
        )
        conn.execute("INSERT INTO templates VALUES ('A', 'alpha content', 1.0, '1,0')")
        conn.execute("INSERT INTO templates VALUES ('B', 'beta content', 0.8, '0,1')")


def test_enhance_creates_report(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setattr("template_engine.workflow_enhancer.validate_enterprise_operation", lambda *_a, **_k: True)
    monkeypatch.setattr(
        "template_engine.workflow_enhancer.DEFAULT_ANALYTICS_DB",
        tmp_path / "analytics.db",
        raising=False,
    )
    db = tmp_path / "prod.db"
    dash = tmp_path / "dash"
    _create_db(db)
    enhancer = TemplateWorkflowEnhancer(db, dash)
    assert enhancer.enhance(timeout_minutes=1)
    report_file = dash / "workflow_enhancement_report.json"
    assert report_file.exists()
    data = json.loads(report_file.read_text())
    assert data["total_templates"] == 2
    assert enhancer.validate_enhancement(2)


def test_enhancer_runs_validator(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setattr(
        "template_engine.workflow_enhancer.validate_enterprise_operation",
        lambda *_a, **_k: True,
    )
    monkeypatch.setattr(
        "template_engine.workflow_enhancer.DEFAULT_ANALYTICS_DB",
        tmp_path / "analytics.db",
        raising=False,
    )
    db = tmp_path / "prod.db"
    dash = tmp_path / "dash"
    _create_db(db)
    import template_engine.workflow_enhancer as we

    dummy = type(
        "D", (), {"called": False, "validate_corrections": lambda self, files: setattr(self, "called", True) or True}
    )()
    monkeypatch.setattr(we, "SecondaryCopilotValidator", lambda: dummy)
    enhancer = TemplateWorkflowEnhancer(db, dash)
    enhancer.enhance(timeout_minutes=1)
    assert dummy.called
