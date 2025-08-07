import pytest
from flask import render_template

TEMPLATES = [
    "dashboard.html",
    "backup_restore.html",
    "database.html",
    "deployment.html",
    "migration.html",
]


@pytest.mark.parametrize("template", TEMPLATES)
def test_templates_include_progress_and_compliance(template, monkeypatch, tmp_path):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    from web_gui.scripts.flask_apps.enterprise_dashboard import app

    with app.test_request_context('/'):
        html = render_template(template, metrics={}, compliance={})
    assert 'id="progress"' in html
    assert "/dashboard/compliance" in html


def test_dashboard_includes_js_module(monkeypatch, tmp_path):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    from web_gui.scripts.flask_apps.enterprise_dashboard import app

    with app.test_request_context('/'):
        html = render_template("dashboard.html", metrics={}, compliance={})
    assert "js/dashboard_intelligence.js" in html


def test_compliance_metrics_template_renders(monkeypatch, tmp_path):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    from web_gui.scripts.flask_apps import enterprise_dashboard as ed

    metrics = {"score": 1.0, "last_audit_date": "2024-01-01", "compliance_trend": [0.9]}
    with ed.app.test_request_context('/'):
        html = render_template("html/compliance_metrics.html", metrics=metrics)
    assert "Compliance Metrics" in html
    assert "table" in html


def test_rollback_logs_template_renders(monkeypatch, tmp_path):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    from web_gui.scripts.flask_apps import enterprise_dashboard as ed

    logs = [{"timestamp": "2024-01-01", "event": "Test"}]
    with ed.app.test_request_context('/'):
        html = render_template("html/rollback_logs.html", logs=logs)
    assert "Rollback Logs" in html
    assert "Test" in html
