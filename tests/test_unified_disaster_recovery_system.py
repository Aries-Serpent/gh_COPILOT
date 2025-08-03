"""Tests for the disaster recovery utility module."""

from __future__ import annotations

import hashlib

from unified_disaster_recovery_system import UnifiedDisasterRecoverySystem
from scripts.utilities import unified_disaster_recovery_system as util_module


def test_scheduler_logs_and_creates_backup(tmp_path, monkeypatch):
    """BackupScheduler should create a backup file and log the event."""

    workspace = tmp_path / "ws"
    workspace.mkdir()
    backup_root = tmp_path / "backup"

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))

    events = []
    monkeypatch.setattr(
        util_module.enterprise_logging, "log_event", lambda e: events.append(e)
    )

    system = UnifiedDisasterRecoverySystem(str(workspace))
    backup_file = system.schedule_backups()

    assert backup_file.exists()
    checksum = backup_file.with_suffix(backup_file.suffix + ".sha256")
    assert checksum.exists()
    assert any(evt["event"] == "backup_scheduled" for evt in events)


def test_restore_executor_verifies_integrity(tmp_path, monkeypatch):
    """RestoreExecutor should restore a backup and log success."""

    workspace = tmp_path / "ws"
    workspace.mkdir()
    backup_root = tmp_path / "backup"
    backup_root.mkdir()

    backup_file = backup_root / "data.txt"
    data = "payload"
    backup_file.write_text(data, encoding="utf-8")
    (backup_root / "data.txt.sha256").write_text(
        hashlib.sha256(data.encode("utf-8")).hexdigest(), encoding="utf-8"
    )

    events = []
    monkeypatch.setattr(
        util_module.enterprise_logging, "log_event", lambda e: events.append(e)
    )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))

    system = UnifiedDisasterRecoverySystem(str(workspace))
    assert system.restore_backup(backup_file)

    restored = workspace / "data.txt"
    assert restored.exists()
    assert restored.read_text() == data
    assert any(evt["event"] == "restore_success" for evt in events)

