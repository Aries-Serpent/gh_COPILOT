"""Regression tests for :class:`artifact_manager.LfsPolicy` session directory metadata."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from artifact_manager import LfsPolicy


def _init_repo(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / ".git").mkdir()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _init_repo(tmp_path)
    return tmp_path


def test_lfs_policy_defaults_when_missing_session_dir(repo: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Missing ``session_artifact_dir`` should fall back to the default directory."""
    policy_file = repo / ".codex_lfs_policy.yaml"
    policy_file.write_text("enable_autolfs: false\n", encoding="utf-8")

    with caplog.at_level(logging.INFO):
        policy = LfsPolicy(repo)

    assert policy.session_artifact_dir == LfsPolicy.DEFAULT_SESSION_DIR
    assert any("session_artifact_dir not specified" in m for m in caplog.messages)


def test_lfs_policy_warns_on_invalid_session_dir(repo: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Non-string ``session_artifact_dir`` values are rejected with a warning."""
    policy_file = repo / ".codex_lfs_policy.yaml"
    policy_file.write_text("session_artifact_dir: 123\n", encoding="utf-8")

    with caplog.at_level(logging.WARNING):
        policy = LfsPolicy(repo)

    assert policy.session_artifact_dir == LfsPolicy.DEFAULT_SESSION_DIR
    assert any("Invalid session_artifact_dir" in m for m in caplog.messages)
