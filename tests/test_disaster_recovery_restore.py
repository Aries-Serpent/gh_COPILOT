from unified_disaster_recovery_system import UnifiedDisasterRecoverySystem


def test_recovery_restores_files(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    backup_root = tmp_path / "backup"
    source = backup_root / "production_backup"
    source.mkdir(parents=True)
    (source / "data.txt").write_text("ok")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))
    system = UnifiedDisasterRecoverySystem(str(workspace))
    assert system.perform_recovery()
    restored = workspace / "restored" / "data.txt"
    assert restored.exists()
    assert restored.read_text() == "ok"
