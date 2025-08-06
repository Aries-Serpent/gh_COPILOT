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


def test_validator_rejects_workspace_inside_backup(monkeypatch, tmp_path):
    """Workspace nested within backup should be rejected."""
    backup = tmp_path / "backup"
    workspace = backup / "ws"
    workspace.mkdir(parents=True)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup))
    validator = AntiRecursionValidator(str(workspace))
    assert not validator.validate_workspace_integrity()


def test_validator_rejects_same_paths(monkeypatch, tmp_path):
    """Identical workspace and backup paths are invalid."""
    workspace = tmp_path / "ws"
    workspace.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(workspace))
    validator = AntiRecursionValidator(str(workspace))
    assert not validator.validate_workspace_integrity()

