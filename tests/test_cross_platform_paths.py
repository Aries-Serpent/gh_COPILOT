#!/usr/bin/env python3
"""Tests for CrossPlatformPathManager."""

from utils.cross_platform_paths import CrossPlatformPathManager


def test_get_workspace_from_env(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    assert CrossPlatformPathManager.get_workspace_path() == tmp_path


def test_backup_root_from_env(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path))
    assert CrossPlatformPathManager.get_backup_root() == tmp_path


def test_workspace_fallback(monkeypatch, tmp_path):
    monkeypatch.delenv("GH_COPILOT_WORKSPACE", raising=False)
    monkeypatch.chdir(tmp_path)
    assert CrossPlatformPathManager.get_workspace_path() == tmp_path


def test_workspace_parent_detection(monkeypatch, tmp_path):
    ws = tmp_path / "gh_COPILOT"
    sub = ws / "subdir"
    sub.mkdir(parents=True)
    monkeypatch.delenv("GH_COPILOT_WORKSPACE", raising=False)
    monkeypatch.chdir(sub)
    assert CrossPlatformPathManager.get_workspace_path() == sub


def test_workspace_env_invalid(monkeypatch, tmp_path):
    missing = tmp_path / "missing"
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(missing))
    monkeypatch.chdir(tmp_path)
    assert CrossPlatformPathManager.get_workspace_path() == tmp_path


def test_backup_defaults_match(monkeypatch):
    """Both helpers should resolve the same default backup directory."""
    monkeypatch.delenv("GH_COPILOT_BACKUP_ROOT", raising=False)
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")
    monkeypatch.setattr(
        "enterprise_modules.compliance.validate_enterprise_operation",
        lambda: None,
    )
    from scripts.database.complete_consolidation_orchestrator import (
        ExternalBackupConfiguration,
    )

    assert CrossPlatformPathManager.get_backup_root() == ExternalBackupConfiguration.get_backup_root()
