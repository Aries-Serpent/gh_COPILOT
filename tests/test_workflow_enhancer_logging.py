import sqlite3
from pathlib import Path

import pytest

from template_engine.workflow_enhancer import TemplateWorkflowEnhancer
import template_engine.workflow_enhancer as workflow_enhancer
from utils import log_utils


def _init_db(db: Path) -> None:
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE templates (template_name TEXT, template_content TEXT, compliance_score REAL, feature_vector TEXT)"
        )
        conn.execute("INSERT INTO templates VALUES ('A', 'alpha', 0.9, '1,0')")


def test_workflow_enhancer_logs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    events = []

    def fake_log(event, **_kw):
        events.append(event)
        return True

    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setattr(workflow_enhancer, "validate_enterprise_operation", lambda *_a, **_k: True)
    monkeypatch.setattr(log_utils, "_log_event", fake_log)
    monkeypatch.setattr(workflow_enhancer, "_log_event", fake_log)
    monkeypatch.setattr(workflow_enhancer, "collect_metrics", lambda: {"cpu_percent": 10.0})
    import dashboard.compliance_metrics_updater as cmu

    monkeypatch.setattr(cmu, "validate_no_recursive_folders", lambda: None)

    db = tmp_path / "prod.db"
    _init_db(db)
    dash = tmp_path / "dash"
    enhancer = TemplateWorkflowEnhancer(db, dash)
    assert enhancer.enhance(timeout_minutes=1)
    assert any(e.get("event") == "workflow_enhancement_start" for e in events)
    assert any(e.get("event") == "workflow_enhancement_complete" for e in events)
    assert any(e.get("event") == "workflow_enhancement_report_generated" for e in events)
