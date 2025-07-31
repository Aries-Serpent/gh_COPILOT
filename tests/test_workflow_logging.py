

from template_engine.workflow_enhancer import TemplateWorkflowEnhancer


def test_workflow_report_logs_event(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setattr(
        "template_engine.workflow_enhancer.validate_enterprise_operation",
        lambda *_a, **_k: True,
    )
    events = []
    monkeypatch.setattr(
        "template_engine.workflow_enhancer._log_event",
        lambda evt, **_: events.append(evt),
    )

    db = tmp_path / "prod.db"
    with open(db, "wb"):
        pass
    dash = tmp_path / "dash"
    enhancer = TemplateWorkflowEnhancer(db, dash)
    enhancer.generate_modular_report([], {}, [], 0.0)

    assert any(e.get("event") == "workflow_report" for e in events)
    report = dash / "workflow_enhancement_report.json"
    assert report.exists()
