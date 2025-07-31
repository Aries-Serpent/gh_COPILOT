
import py7zr
import pytest


def test_archive_backups_creates_archive(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    backup_root = tmp_path / "bk"
    backup_root.mkdir()
    (backup_root / "file.txt").write_text("x")

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))

    from scripts import backup_archiver

    archive_path = backup_archiver.archive_backups()

    assert archive_path.exists()
    with py7zr.SevenZipFile(archive_path) as zf:
        assert "file.txt" in zf.getnames()


def test_archive_backups_disallows_internal_backup(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    backup_root = workspace / "bk"
    backup_root.mkdir()

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))

    from scripts import backup_archiver

    with pytest.raises(RuntimeError):
        backup_archiver.archive_backups()

