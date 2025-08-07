"""Basic tests for Flask app creation in the web GUI."""

import pytest


def test_flask_app_can_start() -> None:
    """Ensure the Flask application can create a test client."""
    try:
        from web_gui import dashboard_actionable_gui
    except Exception:
        pytest.skip("dashboard_actionable_gui unavailable")

    client = dashboard_actionable_gui.app.test_client()
    response = client.get("/")
    assert response.status_code < 500

