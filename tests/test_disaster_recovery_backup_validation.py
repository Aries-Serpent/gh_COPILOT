from unified_disaster_recovery_system import UnifiedDisasterRecoverySystem
import hashlib


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


def test_schedule_backup_creates_checksum(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    backup_root = tmp_path / "backup"
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))
    system = UnifiedDisasterRecoverySystem(str(workspace))

    backup_file = system.schedule_backups()
    assert backup_file.exists()
    hash_file = backup_file.with_suffix(backup_file.suffix + ".sha256")
    assert hash_file.exists()
    digest = hashlib.sha256(backup_file.read_bytes()).hexdigest()
    assert hash_file.read_text().strip() == digest
