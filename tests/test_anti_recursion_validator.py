"""Tests for AntiRecursionValidator integrity checks."""

from scripts.validation.enterprise_dual_copilot_validator import AntiRecursionValidator


def test_validator_rejects_internal_backup(monkeypatch, tmp_path):
    """Validator returns False when backup resides within the workspace."""
    workspace = tmp_path / "ws"
    workspace.mkdir()
    internal_backup = workspace / "backup"
    internal_backup.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(internal_backup))
    validator = AntiRecursionValidator(str(workspace))
    assert not validator.validate_workspace_integrity()


def test_validator_accepts_external_backup(monkeypatch, tmp_path):
    """Validator returns True when backup is outside the workspace."""
    workspace = tmp_path / "ws"
    workspace.mkdir()
    external_backup = tmp_path / "backup"
    external_backup.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(external_backup))
    validator = AntiRecursionValidator(str(workspace))
    assert validator.validate_workspace_integrity()

