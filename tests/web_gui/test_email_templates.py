import pytest
from flask import render_template


@pytest.mark.parametrize(
    "template, context, expected",
    [
        (
            "email/alert_notifications.html",
            {"subject": "Alert", "message": "Attention"},
            ["Alert", "Attention"],
        ),
        (
            "email/deployment_reports.html",
            {"subject": "Deployment", "report": "Success"},
            ["Deployment", "Success"],
        ),
        (
            "email/compliance_reports.html",
            {"subject": "Compliance", "report": "Pass"},
            ["Compliance", "Pass"],
        ),
    ],
)
def test_email_templates_render(template, context, expected, monkeypatch, tmp_path):
    """Ensure email templates render dynamic content."""
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    from web_gui.scripts.flask_apps.enterprise_dashboard import app

    with app.test_request_context('/'):
        html = render_template(template, **context)
    for item in expected:
        assert item in html

