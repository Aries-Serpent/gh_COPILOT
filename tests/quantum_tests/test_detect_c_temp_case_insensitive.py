from pathlib import Path
from unittest import mock

import pytest

from ghc_quantum.optimizers import quantum_optimizer as qo


@pytest.mark.parametrize("workspace", [
    Path("E:/temp/Project"),
    Path("e:/TEMP/project"),
])
def test_detects_workspace_case_insensitive(workspace, tmp_path):
    """Workspace paths under E:/temp are flagged regardless of casing."""
    with mock.patch.object(qo.CrossPlatformPathManager, "get_workspace_path", return_value=workspace), \
         mock.patch.object(qo.CrossPlatformPathManager, "get_backup_root", return_value=tmp_path), \
         mock.patch.object(qo, "_log_violation") as log:
        expected = workspace.as_posix()
        assert qo.detect_c_temp_violations() == expected
        log.assert_called_once_with(expected)


@pytest.mark.parametrize("backup", [
    Path("E:/Temp/backup"),
    Path("e:/temp/BACKUP"),
])
def test_detects_backup_case_insensitive(backup, tmp_path):
    """Backup paths under E:/temp are flagged regardless of casing."""
    ws = tmp_path / "workspace"
    with mock.patch.object(qo.CrossPlatformPathManager, "get_workspace_path", return_value=ws), \
         mock.patch.object(qo.CrossPlatformPathManager, "get_backup_root", return_value=backup), \
         mock.patch.object(qo, "_log_violation") as log:
        expected = backup.as_posix()
        assert qo.detect_c_temp_violations() == expected
        log.assert_called_once_with(expected)
