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

    with app.app_context():
        html = render_template(template, metrics={}, compliance={})
    assert 'id="progress"' in html
    assert "/dashboard/compliance" in html
