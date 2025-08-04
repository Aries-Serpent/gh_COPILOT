import hashlib

from unified_disaster_recovery_system import (
    UnifiedDisasterRecoverySystem,
    restore_backup,
)
from scripts.utilities import unified_disaster_recovery_system as util_module


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


def test_restore_backup_success(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    backup_root = tmp_path / "backup"
    backup_root.mkdir()
    backup_file = backup_root / "data.txt"
    backup_file.write_text("data", encoding="utf-8")
    (backup_root / "data.txt.sha256").write_text(
        hashlib.sha256(backup_file.read_bytes()).hexdigest(), encoding="utf-8"
    )

    events = []
    monkeypatch.setattr(util_module.enterprise_logging, "log_event", lambda e: events.append(e))

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    assert restore_backup(backup_file)
    restored = workspace / "data.txt"
    assert restored.exists()
    assert any(evt["event"] == "restore_success" for evt in events)


def test_restore_backup_hash_mismatch(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    backup_root = tmp_path / "backup"
    backup_root.mkdir()
    backup_file = backup_root / "data.txt"
    backup_file.write_text("data", encoding="utf-8")
    (backup_root / "data.txt.sha256").write_text("bad", encoding="utf-8")

    events = []
    monkeypatch.setattr(util_module.enterprise_logging, "log_event", lambda e: events.append(e))

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    assert not restore_backup(backup_file)
    assert any(evt["event"] == "restore_failed" for evt in events)


def test_restore_backup_missing_checksum(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    backup_root = tmp_path / "backup"
    backup_root.mkdir()
    backup_file = backup_root / "data.txt"
    backup_file.write_text("data", encoding="utf-8")

    events = []
    monkeypatch.setattr(util_module.enterprise_logging, "log_event", lambda e: events.append(e))

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    assert not restore_backup(backup_file)
    assert any(evt["event"] == "restore_failed" for evt in events)
