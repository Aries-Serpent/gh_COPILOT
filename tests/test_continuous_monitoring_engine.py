from pathlib import Path

from scripts.monitoring.continuous_monitoring_engine import ContinuousMonitoringEngine


def test_monitoring_cycle_triggers_auto_remediation(monkeypatch, tmp_path):
    db_file = tmp_path / "production.db"
    db_file.touch()
    engine = ContinuousMonitoringEngine(cycle_seconds=0, workspace=tmp_path, db_path=db_file)

    events = []
    monkeypatch.setattr(engine, "_health_check", lambda: {"cpu_percent": 95, "memory_percent": 95, "anomaly": 1, "note": "high"})
    monkeypatch.setattr(engine.optimizer, "optimize", lambda workspace: events.append("optimize"))
    monkeypatch.setattr(engine.intel, "gather", lambda: events.append("gather"))

    engine.run_cycle([lambda: events.append("action")])

    assert "optimize" in events
    assert "gather" in events
