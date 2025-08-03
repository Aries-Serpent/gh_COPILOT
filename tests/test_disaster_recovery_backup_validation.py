from unified_disaster_recovery_system import UnifiedDisasterRecoverySystem


def test_recovery_rejects_internal_backup(tmp_path, monkeypatch, caplog):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    internal_backup = workspace / "backup"
    internal_backup.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(internal_backup))
    system = UnifiedDisasterRecoverySystem(str(workspace))
    with caplog.at_level("ERROR"):
        assert not system.perform_recovery()
        assert "resides within workspace" in caplog.text
