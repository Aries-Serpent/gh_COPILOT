import os

import pytest

from quantum_optimizer import validate_no_recursive_folders


@pytest.fixture()
def temp_paths(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    backup = tmp_path / "backup"
    workspace.mkdir()
    backup.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup))
    return workspace, backup


def test_permission_error_is_ignored(temp_paths):
    workspace, _ = temp_paths
    restricted = workspace / "restricted"
    restricted.mkdir()
    os.chmod(restricted, 0)
    try:
        validate_no_recursive_folders()
    finally:
        os.chmod(restricted, 0o700)


def test_max_depth_limits_traversal(temp_paths):
    workspace, _ = temp_paths
    deep = workspace / "a" / "b" / "c"
    deep.mkdir(parents=True)
    loop = deep / "loop"
    loop.symlink_to(workspace)
    with pytest.raises(RuntimeError):
        validate_no_recursive_folders()
    try:
        validate_no_recursive_folders(max_depth=2)
    finally:
        loop.unlink()

