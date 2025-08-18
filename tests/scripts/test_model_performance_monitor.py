from __future__ import annotations

import sqlite3
from pathlib import Path

from scripts.ml.deploy_models import deploy_model
from scripts.ml.model_performance_monitor import monitor_metrics


def _make_registry(tmp_path: Path) -> Path:
    registry = tmp_path / "registry"
    (registry / "MyModel" / "1").mkdir(parents=True)
    (registry / "MyModel" / "1" / "model.txt").write_text("v1")
    (registry / "MyModel" / "2").mkdir(parents=True)
    (registry / "MyModel" / "2" / "model.txt").write_text("v2")
    return registry


def test_monitor_metrics_triggers_rollback(tmp_path, monkeypatch):
    registry = _make_registry(tmp_path)
    workspace = tmp_path / "workspace"
    analytics_db = tmp_path / "analytics.db"

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("MODEL_REGISTRY_URI", str(registry))
    monkeypatch.setenv("MODEL_NAME", "MyModel")
    monkeypatch.setenv("MODEL_VERSION", "1")
    monkeypatch.setenv("WEB_DASHBOARD_ENABLED", "1")
    monkeypatch.setenv("ACCURACY_THRESHOLD", "0.9")

    # Deploy version 1 then version 2
    deploy_model(analytics_db=analytics_db)
    monkeypatch.setenv("MODEL_VERSION", "2")
    deploy_model(analytics_db=analytics_db)

    def bad_metrics(model: str, version: str) -> dict[str, float]:
        return {"accuracy": 0.5, "latency": 200.0}

    monitor_metrics(analytics_db=analytics_db, metrics_fetcher=bad_metrics)

    with sqlite3.connect(analytics_db) as conn:
        last_version = conn.execute(
            "SELECT version FROM model_deployments ORDER BY id DESC LIMIT 1"
        ).fetchone()[0]
        assert last_version == "1"

        alert = conn.execute("SELECT db, table_name FROM dashboard_alerts").fetchone()
        assert alert == ("MyModel", "accuracy")

        rollback = conn.execute(
            "SELECT target, backup FROM rollback_logs"
        ).fetchone()
        assert rollback == ("MyModel", "1")

