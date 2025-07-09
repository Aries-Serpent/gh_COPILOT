from types import SimpleNamespace

import pytest

import unified_monitoring_optimization_system as umos_module


class DummyTqdm:
    def __init__(self, *args, **kwargs):
        pass

    def set_description(self, desc):
        pass

    def update(self, value):
        pass

    def close(self):
        pass


def test_collect_metrics(tmp_path, monkeypatch):
    monkeypatch.setattr(]
       lambda interval=1: 10.0)
            monkeypatch.setattr(]
            lambda: SimpleNamespace(percent=20.0))
            monkeypatch.setattr(]
            lambda p: SimpleNamespace(percent=30.0))
            monkeypatch.setattr(]
            lambda: SimpleNamespace(bytes_sent=100, bytes_recv=200))
            monkeypatch.setattr(umos_module.psutil, "pids", lambda: [1, 2, 3])

            system = umos_module.UnifiedMonitoringOptimizationSystem(]
        workspace_root =str(tmp_path))
            metrics = system.collect_metrics()

            assert metrics.cpu_percent == 10.0
            assert metrics.memory_percent == 20.0
            assert metrics.disk_usage_percent == 30.0
            assert metrics.database_connections == 1
            count = system.metrics_db.execute(]
            "SELECT COUNT(*) FROM performance_metrics").fetchone()[0]
            assert count == 1


            def test_optimize_system(tmp_path, monkeypatch):
    monkeypatch.setattr(umos_module.time, "sleep", lambda x: None)
    monkeypatch.setattr(umos_module, "tqdm", DummyTqdm)

    system = umos_module.UnifiedMonitoringOptimizationSystem(]
        workspace_root =str(tmp_path))
    summary = system.optimize_system()

    assert summary.final_efficiency == 100.0
    assert summary.phases_completed == 4
