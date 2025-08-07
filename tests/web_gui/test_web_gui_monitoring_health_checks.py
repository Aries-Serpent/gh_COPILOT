from __future__ import annotations

from web_gui.monitoring.health_checks import (
    check_compliance_status,
    check_database_connection,
    check_quantum_score,
    check_system_resources,
    check_template_rendering,
)
from web_gui.monitoring.performance_metrics import collect_performance_metrics
from web_gui.monitoring.alerting.escalation_rules import get_escalation_level
from web_gui.monitoring.alerting.alert_manager import trigger_alert


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


def test_check_system_resources_true() -> None:
    assert check_system_resources(100.0, 100.0)


def test_check_compliance_status() -> None:
    assert check_compliance_status({"policy": "p", "status": "ok"})


def test_check_quantum_score() -> None:
    assert check_quantum_score([0.1, 0.2], threshold=0.0)


def test_trigger_alert_returns_level() -> None:
    messages = []
    level = trigger_alert("hello", "critical", messages.append)
    assert level == "high"
    assert messages and messages[0].startswith("[HIGH]")
