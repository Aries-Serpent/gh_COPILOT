"""Simple end-to-end style tests."""

import pytest


def test_root_endpoint() -> None:
    """The root endpoint should respond without server errors."""
    try:
        from web_gui import dashboard_actionable_gui
    except Exception:
        pytest.skip("dashboard_actionable_gui unavailable")

    client = dashboard_actionable_gui.app.test_client()
    assert client.get("/").status_code < 500


def test_missing_endpoint_returns_404() -> None:
    """Unknown endpoints should return 404."""
    try:
        from web_gui import dashboard_actionable_gui
    except Exception:
        pytest.skip("dashboard_actionable_gui unavailable")

    client = dashboard_actionable_gui.app.test_client()
    assert client.get("/missing").status_code == 404

