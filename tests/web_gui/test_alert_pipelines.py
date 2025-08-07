from __future__ import annotations

from web_gui.monitoring.alerting import NOTIFICATION_LOG, ROUTE_LOG, trigger_alert


def test_critical_pipeline_routes_to_dashboard() -> None:
    NOTIFICATION_LOG.clear()
    ROUTE_LOG.clear()
    trigger_alert("system failure", "critical")
    assert NOTIFICATION_LOG == ["[HIGH] system failure"]
    assert ROUTE_LOG == [("high", "system failure")]


def test_warning_pipeline_no_dashboard_route() -> None:
    NOTIFICATION_LOG.clear()
    ROUTE_LOG.clear()
    trigger_alert("minor issue", "warning")
    assert NOTIFICATION_LOG == ["[MEDIUM] minor issue"]
    assert ROUTE_LOG == []
