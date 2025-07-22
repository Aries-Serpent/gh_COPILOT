#!/usr/bin/env python3
"""Tests for CrossPlatformPathManager."""

from pathlib import Path
from utils.cross_platform_paths import CrossPlatformPathManager


def test_get_workspace_from_env(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    assert CrossPlatformPathManager.get_workspace_path() == tmp_path


def test_backup_root_from_env(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path))
    assert CrossPlatformPathManager.get_backup_root() == tmp_path


def test_workspace_defaults_to_cwd(monkeypatch):
    """Workspace path falls back to current directory when env var unset."""
    monkeypatch.delenv("GH_COPILOT_WORKSPACE", raising=False)
    assert CrossPlatformPathManager.get_workspace_path() == Path.cwd()
