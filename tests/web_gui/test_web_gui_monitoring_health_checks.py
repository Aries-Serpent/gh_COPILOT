from __future__ import annotations

from web_gui.monitoring.health_checks import (
    check_cache_status,
    check_compliance_status,
    check_database_connection,
    check_quantum_score,
    get_service_uptime,
    check_system_resources,
    check_template_rendering,
    run_all_checks,
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


def test_check_cache_status_true() -> None:
    assert check_cache_status({})


def test_get_service_uptime_positive() -> None:
    assert get_service_uptime() >= 0


def test_trigger_alert_returns_level() -> None:
    messages: list[str] = []
    routed: list[tuple[str, str]] = []
    pipeline = [
        lambda lvl, msg: messages.append(f"[{lvl.upper()}] {msg}"),
        lambda lvl, msg: routed.append((lvl, msg)),
    ]
    level = trigger_alert("hello", "critical", pipeline=pipeline)
    assert level == "high"
    assert messages and messages[0].startswith("[HIGH]")
    assert routed == [("high", "hello")]


def test_run_all_checks_alerts_on_failure() -> None:
    messages: list[str] = []
    routed: list[tuple[str, str]] = []
    results = run_all_checks(
        compliance_data={},
        cache={},
        alert=True,
        notifier=messages.append,
        dashboard_router=lambda lvl, msg: routed.append((lvl, msg)),
    )
    assert results["compliance"] is False
    assert results["cache"] is True
    assert "uptime" in results and results["uptime"] >= 0
    assert messages and messages[0].startswith("[HIGH]")
    assert routed == [("high", "compliance check failed")]
