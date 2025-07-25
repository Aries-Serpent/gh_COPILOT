#!/usr/bin/env python3
"""Tests for CrossPlatformPathManager."""

from scripts.database.complete_consolidation_orchestrator import (
    ExternalBackupConfiguration,
)
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


def test_backup_root_default(monkeypatch):
    """ExternalBackupConfiguration matches CrossPlatformPathManager default."""
    monkeypatch.delenv("GH_COPILOT_BACKUP_ROOT", raising=False)
    backup1 = ExternalBackupConfiguration.get_backup_root()
    backup2 = CrossPlatformPathManager.get_backup_root()
    assert backup1 == backup2
