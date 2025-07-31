def test_validate_enterprise_operation_rejects_internal_backup(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    backup_root = workspace / "bk"
    backup_root.mkdir()

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))

    from enterprise_modules.compliance import validate_enterprise_operation

    assert not validate_enterprise_operation(str(backup_root))


def test_validate_enterprise_operation_allows_external_backup(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    backup_root = tmp_path / "bk"
    backup_root.mkdir()

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))

    from enterprise_modules.compliance import validate_enterprise_operation

    assert validate_enterprise_operation(str(workspace / "data")) is True


def test_validate_enterprise_operation_allows_opt_backup(tmp_path, monkeypatch):
    """Ensure /opt/gh_COPILOT_backup is not treated as inside workspace."""
    workspace = tmp_path / "ws"
    workspace.mkdir()

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", "/opt/gh_COPILOT_backup")

    from enterprise_modules.compliance import validate_enterprise_operation

    assert validate_enterprise_operation(str(workspace / "data")) is True
