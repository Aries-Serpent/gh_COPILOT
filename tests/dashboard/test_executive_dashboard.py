"""Tests for the executive dashboard analytics collection."""

from web_gui.dashboards.executive_dashboard import collect_analytics


def test_collect_analytics_keys() -> None:
    """Ensure analytics dictionary contains expected keys."""
    data = collect_analytics()
    required = {"technical", "security", "quantum", "performance"}
    assert required.issubset(data.keys())
    for key in required:
        assert isinstance(data[key], dict)

