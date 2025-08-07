"""Tests for the executive dashboard analytics collection."""

from web_gui.dashboards.executive_dashboard import collect_analytics


def test_collect_analytics_keys() -> None:
    """Ensure analytics dictionary contains expected keys."""
    data = collect_analytics()
    assert set(data.keys()) == {"technical", "security", "quantum"}
    for section in data.values():
        assert isinstance(section, dict)

