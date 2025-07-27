from pathlib import Path

import pytest


def test_validate_enterprise_operation_rejects_internal_backup(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    backup_root = workspace / "bk"
    backup_root.mkdir()

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))

    from db_tools.utils.enterprise_validation import validate_enterprise_operation

    with pytest.raises(RuntimeError):
        validate_enterprise_operation(str(backup_root))


def test_validate_enterprise_operation_allows_external_backup(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    backup_root = tmp_path / "bk"
    backup_root.mkdir()

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))

    from db_tools.utils.enterprise_validation import validate_enterprise_operation

    assert validate_enterprise_operation(str(workspace / "data")) is True

