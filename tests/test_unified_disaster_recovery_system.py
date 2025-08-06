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
    assert any(evt["description"] == "backup_scheduled" for evt in events)


def test_restore_executor_verifies_integrity(tmp_path, monkeypatch):
    """RestoreExecutor should restore a backup and log success."""

    workspace = tmp_path / "ws"
    workspace.mkdir()
    backup_root = tmp_path / "backup"
    backup_root.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))

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

    system = UnifiedDisasterRecoverySystem(str(workspace))
    assert system.restore_backup(backup_file)

    restored = workspace / "data.txt"
    assert restored.exists()
    assert restored.read_text() == data
    assert any(evt["description"] == "restore_success" for evt in events)


def test_retention_policy_prunes_old_backups(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    backup_root = tmp_path / "backup"
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))

    import datetime as dt

    times = [
        dt.datetime(2020, 1, 1, 0, 0, 0),
        dt.datetime(2020, 1, 1, 0, 0, 1),
        dt.datetime(2020, 1, 1, 0, 0, 2),
    ]

    monkeypatch.setattr(util_module, "datetime", type("_dt", (), {"utcnow": lambda: times.pop(0)}))

    system = UnifiedDisasterRecoverySystem(str(workspace))
    first = system.schedule_backups(max_backups=2)
    system.schedule_backups(max_backups=2)
    system.schedule_backups(max_backups=2)

    backups = list(backup_root.glob("scheduled_backup_*.bak"))
    assert len(backups) == 2
    assert first not in backups


def test_schedule_uses_default_retention(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    backup_root = tmp_path / "backup"
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))

    import datetime as dt

    times = [dt.datetime(2020, 1, 1, 0, 0, i) for i in range(util_module.DEFAULT_MAX_BACKUPS + 1)]
    monkeypatch.setattr(util_module, "datetime", type("_dt", (), {"utcnow": lambda: times.pop(0)}))

    system = UnifiedDisasterRecoverySystem(str(workspace))
    for _ in range(util_module.DEFAULT_MAX_BACKUPS + 1):
        system.schedule_backups()

    backups = list(backup_root.glob("scheduled_backup_*.bak"))
    assert len(backups) == util_module.DEFAULT_MAX_BACKUPS


def test_cli_schedule_and_restore_logs_to_db(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    backup_root = tmp_path / "backup"
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))
    db_path = tmp_path / "analytics.db"
    monkeypatch.setenv("ANALYTICS_DB", str(db_path))
    orig_log_event = util_module.enterprise_logging.log_event

    def _log_event(event, *, table=util_module.enterprise_logging.DEFAULT_LOG_TABLE, db_path=db_path):
        orig_log_event(event, table=table, db_path=db_path)

    monkeypatch.setattr(util_module.enterprise_logging, "log_event", _log_event)

    assert util_module.main(["--schedule"]) == 0
    backup_file = next(backup_root.glob("scheduled_backup_*.bak"))
    assert util_module.main(["--restore", str(backup_file)]) == 0

    import sqlite3

    with sqlite3.connect(db_path) as conn:
        events = {row[0] for row in conn.execute("SELECT description FROM event_log")}

    assert "backup_scheduled" in events
    assert "restore_success" in events


def test_restore_rejects_untrusted_path(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    backup_root = tmp_path / "backup"
    backup_root.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))

    data = "payload"
    backup_file = workspace / "data.bak"
    backup_file.write_text(data, encoding="utf-8")
    (workspace / "data.bak.sha256").write_text(
        hashlib.sha256(data.encode("utf-8")).hexdigest(), encoding="utf-8"
    )

    events = []
    monkeypatch.setattr(
        util_module.enterprise_logging, "log_event", lambda e: events.append(e)
    )

    system = UnifiedDisasterRecoverySystem(str(workspace))
    assert not system.restore_backup(backup_file)
    assert any(evt["description"] == "restore_failed" for evt in events)


def test_compliance_logger_emits_global_event(monkeypatch):
    events = []
    monkeypatch.setattr(
        util_module.enterprise_logging, "log_event", lambda e: events.append(e)
    )
    called = {}
    monkeypatch.setattr(
        util_module, "log_backup_event", lambda *a, **k: called.setdefault("ok", True)
    )

    logger = util_module.ComplianceLogger()
    logger.log("test_event")

    assert events and events[0]["description"] == "test_event"
    assert called.get("ok")

