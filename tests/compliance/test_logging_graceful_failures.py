import sqlite3

from enterprise_modules import compliance


def test_log_violation_db_failure(monkeypatch):
    def fail_connect(*args, **kwargs):
        raise sqlite3.OperationalError("db down")

    monkeypatch.setattr(compliance, "ensure_violation_logs", lambda *a, **k: None)
    monkeypatch.setattr(compliance.sqlite3, "connect", fail_connect)
    alerts = []
    monkeypatch.setattr(compliance, "send_dashboard_alert", lambda data: alerts.append(data))
    logs = []
    monkeypatch.setattr(compliance.logging, "error", lambda *args, **kwargs: logs.append(args[0] if args else ""))

    compliance._log_violation("test_violation")

    assert alerts, "dashboard alert not sent on db failure"
    assert logs, "error not logged on db failure"


def test_log_rollback_db_failure(monkeypatch):
    def fail_connect(*args, **kwargs):
        raise sqlite3.OperationalError("db down")

    monkeypatch.setattr(compliance, "ensure_rollback_logs", lambda *a, **k: None)
    monkeypatch.setattr(compliance.sqlite3, "connect", fail_connect)
    alerts = []
    monkeypatch.setattr(compliance, "send_dashboard_alert", lambda data: alerts.append(data))
    logs = []
    monkeypatch.setattr(compliance.logging, "error", lambda *args, **kwargs: logs.append(args[0] if args else ""))

    compliance._log_rollback("target", "backup")

    assert alerts, "dashboard alert not sent on db failure"
    assert logs, "error not logged on db failure"
