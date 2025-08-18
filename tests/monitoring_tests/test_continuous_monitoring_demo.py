import sqlite3
from pathlib import Path

import pytest

from scripts.monitoring.continuous_monitoring_system import ContinuousMonitoringSystem


def _prepare_workspace(tmp_path: Path) -> Path:
    (tmp_path / "databases").mkdir()
    db = tmp_path / "databases" / "flake8_violations.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE violations (status TEXT, file_path TEXT, error_code TEXT)"
        )
        conn.execute(
            "INSERT INTO violations (status, file_path, error_code) VALUES ('pending', 'a.py', 'E001')"
        )
        conn.commit()
    return tmp_path


def test_run_monitoring_demo_uses_lockfile(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    workspace = _prepare_workspace(tmp_path)
    monkeypatch.chdir(workspace)

    def dummy_push(metrics, *_, **__):
        pass

    monkeypatch.setattr(
        "scripts.monitoring.continuous_monitoring_system.push_metrics", dummy_push
    )

    cms = ContinuousMonitoringSystem(workspace_path=str(workspace))
    cms.run_monitoring_demo(duration_minutes=0)
    lock = workspace / "monitoring" / "monitoring.lock"
    assert not lock.exists()
    lock.write_text("x")
    with pytest.raises(RuntimeError):
        cms.run_monitoring_demo(duration_minutes=0)


def test_run_monitoring_demo_pushes_dashboard_metrics(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    workspace = _prepare_workspace(tmp_path)
    monkeypatch.chdir(workspace)
    monkeypatch.setenv("WEB_DASHBOARD_ENABLED", "1")
    cms = ContinuousMonitoringSystem(workspace_path=str(workspace))

    pushed: dict[str, float] = {}
    dashboard: dict[str, float] = {}

    def fake_push(metrics, *_, **__):
        pushed.update(metrics)

    def fake_dash(metrics):
        dashboard.update(metrics)

    monkeypatch.setattr(
        "scripts.monitoring.continuous_monitoring_system.push_metrics", fake_push
    )
    monkeypatch.setattr(
        "scripts.monitoring.continuous_monitoring_system._update_dashboard",
        fake_dash,
    )

    cms.run_monitoring_demo(duration_minutes=0)
    assert pushed
    assert dashboard == pushed
