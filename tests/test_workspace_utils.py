#!/usr/bin/env python3

import logging
from pathlib import Path

from copilot.common.workspace_utils import (_within_workspace,
                                            get_workspace_path)


def test_env_var_used(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    assert get_workspace_path() == tmp_path


def test_cwd_fallback(monkeypatch):
    monkeypatch.delenv("GH_COPILOT_WORKSPACE", raising=False)
    assert get_workspace_path() == Path.cwd()


def test_within_workspace(tmp_path):
    file_inside = tmp_path / "a" / "b.txt"
    file_inside.parent.mkdir(parents=True)
    file_inside.touch()
    assert _within_workspace(file_inside, tmp_path)
    outside = Path("/tmp") / "other.txt"
    assert not _within_workspace(outside, tmp_path)
