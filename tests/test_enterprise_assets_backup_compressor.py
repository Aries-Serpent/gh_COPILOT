import importlib
import zipfile
from pathlib import Path

import pytest


def get_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    import enterprise_modules.compliance as coo
    import scripts.database.enterprise_assets_backup_compressor as mod

    importlib.reload(coo)
    return importlib.reload(mod)


def test_compress_assets_backup_creates_zip(tmp_path: Path, monkeypatch) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    source = workspace / "assets"
    source.mkdir()
    (source / "file.txt").write_text("data")

    backup_root = tmp_path / "backups"
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))
    mod = get_module(monkeypatch)
    monkeypatch.setattr(mod, "validate_enterprise_operation", lambda: True)

    dest = mod.compress_assets_backup(workspace, source, backup_name="test.zip")

    assert dest.exists()
    assert dest.parent == backup_root / workspace.name
    with zipfile.ZipFile(dest) as zf:
        assert "file.txt" in zf.namelist()


def test_compress_assets_backup_prevents_workspace_location(tmp_path: Path, monkeypatch) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    source = workspace / "assets"
    source.mkdir()
    (source / "f.txt").write_text("x")

    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(workspace / "backups"))
    mod = get_module(monkeypatch)
    monkeypatch.setattr(mod, "validate_enterprise_operation", lambda: True)

    with pytest.raises(RuntimeError):
        mod.compress_assets_backup(workspace, source, backup_name="bad.zip")
