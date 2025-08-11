from pathlib import Path


def test_compliance_tab_links_api():
    html = Path("dashboard/templates/dashboard.html").read_text()
    assert "/api/compliance_scores" in html

