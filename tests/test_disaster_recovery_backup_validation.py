from unified_disaster_recovery_system import (
    UnifiedDisasterRecoverySystem,
    restore_backup,
)
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
    backup_root.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))
    system = UnifiedDisasterRecoverySystem(str(workspace))

    backup_file = system.schedule_backups()
    assert backup_file.exists()
    hash_file = backup_file.with_suffix(backup_file.suffix + ".sha256")
    assert hash_file.exists()
    digest = hashlib.sha256(backup_file.read_bytes()).hexdigest()
    assert hash_file.read_text().strip() == digest


def test_backup_invocation_on_core_databases(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    db_dir = workspace / "databases"
    db_dir.mkdir(parents=True)
    (db_dir / "production.db").write_text("prod")
    (db_dir / "analytics.db").write_text("analytics")
    backup_root = tmp_path / "backup"
    backup_root.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))

    calls = []

    def fake_schedule(self, max_backups=None):  # noqa: ANN001
        calls.append(True)
        backup_file = backup_root / "dummy.bak"
        backup_file.write_text("backup")
        return backup_file

    monkeypatch.setattr(
        "unified_disaster_recovery_system.BackupScheduler.schedule", fake_schedule
    )
    system = UnifiedDisasterRecoverySystem(str(workspace))
    backup_file = system.schedule_backups()
    assert calls and backup_file.exists()


def test_restore_rejects_untrusted_path(tmp_path, monkeypatch, caplog):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    backup_root = tmp_path / "backup"
    backup_root.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))

    bad_backup = tmp_path / "bad.bak"
    bad_backup.write_text("bad")
    bad_backup.with_suffix(bad_backup.suffix + ".sha256").write_text(
        hashlib.sha256(bad_backup.read_bytes()).hexdigest()
    )

    with caplog.at_level("ERROR"):
        assert not restore_backup(bad_backup)
        assert "outside backup root" in caplog.text
