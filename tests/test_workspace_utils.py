import os
from pathlib import Path

from copilot.common.workspace_utils import get_workspace_path


def test_env_var_used(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    assert get_workspace_path() == tmp_path


def test_cwd_fallback(monkeypatch):
    monkeypatch.delenv("GH_COPILOT_WORKSPACE", raising=False)
    assert get_workspace_path() == Path.cwd()
