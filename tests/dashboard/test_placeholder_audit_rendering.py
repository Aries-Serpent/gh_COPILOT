from pathlib import Path


def test_placeholder_chart_uses_new_endpoint():
    content = Path("dashboard/static/placeholder_chart.js").read_text()
    assert "/api/placeholder_audit" in content
    assert "placeholderOpenCount" in content
    assert "title" in content  # tooltip support


def test_dashboard_template_includes_counts():
    content = Path("dashboard/templates/dashboard.html").read_text()
    assert 'id="placeholderOpenCount"' in content
    assert '<th>Type</th>' in content
