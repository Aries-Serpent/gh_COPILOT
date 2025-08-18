from __future__ import annotations

import unified_monitoring_optimization_system as umo
from unified_monitoring_optimization_system import (
    anomaly_detection_loop,
    register_hook,
)


def test_registered_hooks_feed_anomaly_detection_loop(monkeypatch, tmp_path):
    recorded = []
    monkeypatch.setattr(umo, "_METRIC_HOOKS", [])
    monkeypatch.setattr(umo, "push_metrics", lambda metrics, *a, **k: recorded.append(metrics))
    monkeypatch.setattr(umo, "detect_anomalies", lambda *a, **k: [])
    monkeypatch.setattr(umo, "auto_heal_session", lambda *a, **k: None)

    register_hook(lambda: {"hook_metric": 42.0})

    anomaly_detection_loop(iterations=1, db_path=tmp_path / "a.db", model_path=tmp_path / "m.pkl")
    assert recorded and "hook_metric" in recorded[0]
