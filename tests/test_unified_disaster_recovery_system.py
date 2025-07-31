import logging
from unified_disaster_recovery_system import UnifiedDisasterRecoverySystem


def _create_backup_structure(root):
    prod = root / "production_backup"
    prod.mkdir(parents=True)
    (prod / "sample.txt").write_text("data")


def test_recovery_from_external_backup(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    bk = tmp_path / "bk"
    ws.mkdir()
    bk.mkdir()
    _create_backup_structure(bk)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(ws))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(bk))
    system = UnifiedDisasterRecoverySystem(str(ws))
    assert system.perform_recovery()
    restored = ws / "restored" / "sample.txt"
    assert restored.exists()


def test_recovery_aborts_when_backup_inside_workspace(tmp_path, monkeypatch, caplog):
    ws = tmp_path / "ws"
    bk = ws / "bk"
    ws.mkdir()
    bk.mkdir()
    _create_backup_structure(bk)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(ws))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(bk))
    caplog.set_level(logging.ERROR)
    system = UnifiedDisasterRecoverySystem(str(ws))
    assert not system.perform_recovery()
    assert "cannot reside within workspace" in caplog.text
