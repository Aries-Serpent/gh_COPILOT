import os
from pathlib import Path

from utils.cross_platform_paths import migrate_hard_coded_paths, CrossPlatformPathManager


def test_migrate_creates_backup(tmp_path, monkeypatch):
    file_path = tmp_path / "sample.py"
    file_path.write_text('path = "E:/gh_COPILOT"')

    backup_root = tmp_path / "backups"
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))

    result = migrate_hard_coded_paths(file_path)

    expected_backup = backup_root / "migration_backups" / "sample.py.backup"
    assert result["backup_created"] == str(expected_backup)
    assert expected_backup.exists()

    updated_content = file_path.read_text()
    assert "CrossPlatformPathManager.get_workspace_path()" in updated_content
