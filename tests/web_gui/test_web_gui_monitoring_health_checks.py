from __future__ import annotations

from web_gui.monitoring.health_checks import (
    check_compliance_data,
    check_database_connection,
    check_performance_thresholds,
    check_quantum_score,
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


def test_check_performance_thresholds():
    assert check_performance_thresholds(100, 100)


def test_check_compliance_data():
    data = {"policy": "A", "status": "ok"}
    assert check_compliance_data(data)


def test_check_quantum_score():
    assert check_quantum_score([0.1, 0.2, 0.3], threshold=0.0)


def test_trigger_alert(capsys):
    level = trigger_alert("msg", "warning")
    captured = capsys.readouterr()
    assert "msg" in captured.out
    assert level == "medium"
