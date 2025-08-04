"""Tests for :mod:`disaster_recovery_orchestrator`."""

from __future__ import annotations

from disaster_recovery_orchestrator import DisasterRecoveryOrchestrator


def test_orchestrator_runs_backup_and_recovery(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    backup_root = tmp_path / "backup"
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))

    orchestrator = DisasterRecoveryOrchestrator(str(workspace))
    backup_file = orchestrator.run_backup_cycle()
    assert backup_file.exists()

    assert orchestrator.run_recovery_cycle(backup_file)
    restored = workspace / backup_file.name
    assert restored.exists()


__all__ = ["test_orchestrator_runs_backup_and_recovery"]

