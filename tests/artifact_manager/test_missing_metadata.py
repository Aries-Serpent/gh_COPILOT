"""Tests for edge cases in :mod:`artifact_manager` handling corrupt archives.

This reproduces the scenario where a session archive is present but lacks the
necessary ZIP metadata. The recovery helper should not crash and instead log a
clear error while returning ``None``.
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path

import pytest

from artifact_manager import LfsPolicy, recover_latest_session


def _init_repo(path: Path) -> None:
    """Initialise a minimal git repository at ``path``."""

    subprocess.run(["git", "init"], cwd=path, check=True, stdout=subprocess.DEVNULL)
    (path / "README.md").write_text("init", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=path,
        check=True,
        stdout=subprocess.DEVNULL,
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """Provide a temporary git repository for tests."""

    _init_repo(tmp_path)
    return tmp_path


def test_recover_latest_session_handles_corrupt_archive(
    repo: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Recovery should gracefully handle archives missing ZIP metadata."""

    sessions_dir = repo / "codex_sessions"
    sessions_dir.mkdir()
    bad_archive = sessions_dir / "codex-session_20240101_000000.zip"
    bad_archive.write_text("not a zip", encoding="utf-8")

    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()

    with caplog.at_level(logging.ERROR):
        result = recover_latest_session(tmp_dir, repo, LfsPolicy(repo))

    assert result is None
    assert any("Failed to extract" in message for message in caplog.messages)

