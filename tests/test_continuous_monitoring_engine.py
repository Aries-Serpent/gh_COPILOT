import logging
import sqlite3

from scripts.monitoring.continuous_monitoring_engine import (
    ContinuousMonitoringEngine,
    main,
)


def test_monitoring_cycle_triggers_auto_remediation(monkeypatch, tmp_path):
    db_file = tmp_path / "production.db"
    db_file.touch()
    engine = ContinuousMonitoringEngine(cycle_seconds=0, workspace=tmp_path, db_path=db_file)

    events = []
    monkeypatch.setattr(
        engine, "_health_check", lambda: {"cpu_percent": 95, "memory_percent": 95, "anomaly": 1, "note": "high"}
    )
    monkeypatch.setattr(engine.optimizer, "optimize", lambda workspace: events.append("optimize"))
    monkeypatch.setattr(engine.intel, "gather", lambda: events.append("gather"))

    engine.run_cycle([lambda: events.append("action")])

    assert "optimize" in events
    assert "gather" in events


def test_cli_runs_orchestrated_cycles(monkeypatch, tmp_path):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))

    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    (db_dir / "production.db").touch()

    calls = []

    class DummyOrchestrator:
        def __init__(self, logger=None) -> None:
            pass

        def run(self, primary, targets):
            calls.append("run")
            primary()
            return True, True, {}

    monkeypatch.setattr(
        "scripts.monitoring.continuous_monitoring_engine.DualCopilotOrchestrator",
        DummyOrchestrator,
    )

    monkeypatch.setattr(
        "scripts.monitoring.continuous_monitoring_engine.ContinuousMonitoringEngine.run_cycle",
        lambda self, actions=None: calls.append("cycle"),
    )

    assert main(["--cycles", "2", "--interval", "0"]) == 0
    assert calls.count("cycle") == 2


def test_run_cycle_handles_db_failure(monkeypatch, tmp_path, caplog):
    db_file = tmp_path / "production.db"
    db_file.touch()
    engine = ContinuousMonitoringEngine(cycle_seconds=0, workspace=tmp_path, db_path=db_file)

    monkeypatch.setattr(engine, "_health_check", lambda: {"anomaly": 1, "note": "x"})

    def fail_optimize(workspace):
        raise OSError("disk error")

    def fail_gather():
        raise sqlite3.Error("read error")

    monkeypatch.setattr(engine.optimizer, "optimize", fail_optimize)
    monkeypatch.setattr(engine.intel, "gather", fail_gather)

    caplog.set_level(logging.ERROR)
    engine.run_cycle([])

    assert any("Auto-remediation failed" in r.message for r in caplog.records)


def test_cycle_logs_and_posts(monkeypatch, tmp_path):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    analytics_db = db_dir / "analytics.db"
    (tmp_path / "production.db").touch()
    engine = ContinuousMonitoringEngine(
        cycle_seconds=0, workspace=tmp_path, dashboard_endpoint="http://dash"
    )
    monkeypatch.setattr(
        engine,
        "_health_check",
        lambda: {"cpu_percent": 10.0, "memory_percent": 20.0, "anomaly": 0, "note": ""},
    )

    calls = {}

    def fake_post(url, json, timeout):
        calls["url"] = url
        calls["json"] = json
        return object()

    monkeypatch.setattr(
        "scripts.monitoring.continuous_monitoring_engine.requests.post", fake_post
    )

    engine.run_cycle([])

    with sqlite3.connect(analytics_db) as conn:
        row = conn.execute(
            "SELECT cpu_percent, memory_percent FROM monitoring_cycles"
        ).fetchone()

    assert row == (10.0, 20.0)
    assert calls["url"] == "http://dash"
    assert calls["json"]["cpu_percent"] == 10.0
