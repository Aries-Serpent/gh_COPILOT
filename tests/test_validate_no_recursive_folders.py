from unittest import mock
import quantum_optimizer as qo


def test_validate_no_recursive_folders_normal(tmp_path):
    ws = tmp_path / "ws"
    bk = tmp_path / "bk"
    ws.mkdir()
    bk.mkdir()
    with mock.patch("quantum_optimizer.CrossPlatformPathManager.get_workspace_path", return_value=ws), \
         mock.patch("quantum_optimizer.CrossPlatformPathManager.get_backup_root", return_value=bk):
        assert qo.validate_no_recursive_folders()


def test_validate_no_recursive_folders_nested(tmp_path):
    ws = tmp_path / "ws"
    bk = ws / "bk"
    ws.mkdir()
    bk.mkdir()
    with mock.patch("quantum_optimizer.CrossPlatformPathManager.get_workspace_path", return_value=ws), \
         mock.patch("quantum_optimizer.CrossPlatformPathManager.get_backup_root", return_value=bk):
        assert qo.validate_no_recursive_folders() is False


def test_validate_no_recursive_folders_symlink(tmp_path):
    ws = tmp_path / "ws"
    bk = tmp_path / "bk"
    ws.mkdir()
    bk.mkdir()
    (ws / "bk_link").symlink_to(bk)
    with mock.patch("quantum_optimizer.CrossPlatformPathManager.get_workspace_path", return_value=ws), \
         mock.patch("quantum_optimizer.CrossPlatformPathManager.get_backup_root", return_value=bk):
        assert qo.validate_no_recursive_folders() is False


def test_validate_no_recursive_folders_symlink_in_backup(tmp_path):
    ws = tmp_path / "ws"
    bk = tmp_path / "bk"
    ws.mkdir()
    bk.mkdir()
    (bk / "ws_link").symlink_to(ws)
    with mock.patch("quantum_optimizer.CrossPlatformPathManager.get_workspace_path", return_value=ws), \
         mock.patch("quantum_optimizer.CrossPlatformPathManager.get_backup_root", return_value=bk):
        assert qo.validate_no_recursive_folders() is False
