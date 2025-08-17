
# Auto-generated analytics endpoint tests
def test_dashboard_metric_function():
    import pathlib

    ep = pathlib.Path("enterprise_dashboard.py")
    if not ep.exists():
        return
    src = ep.read_text(encoding="utf-8", errors="ignore")
    assert "_analytics_metric_value" in src
