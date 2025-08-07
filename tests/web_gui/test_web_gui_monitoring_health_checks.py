from __future__ import annotations

from web_gui.monitoring.health_checks import (
    check_database_connection,
    check_template_rendering,
)
from web_gui.monitoring.performance_metrics import collect_performance_metrics
from web_gui.monitoring.alerting.escalation_rules import get_escalation_level


def test_check_database_connection():
    assert check_database_connection()


def test_check_template_rendering():
    assert check_template_rendering("dashboard.html")


def test_collect_performance_metrics_keys():
    metrics = collect_performance_metrics()
    assert "cpu_percent" in metrics
    assert "memory_percent" in metrics


def test_escalation_rules_default():
    assert get_escalation_level("critical") == "high"
