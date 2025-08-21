"""Edge case tests for :mod:`artifact_manager` helpers."""

from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path

import pytest

from artifact_manager import LfsPolicy, check_directory_health, recover_latest_session


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


def test_check_directory_health_rejects_symlink(
    repo: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Symlinks should be rejected to avoid path traversal."""

    target = repo / "real"
    target.mkdir()
    link = repo / "link"
    link.symlink_to(target)

    with caplog.at_level(logging.ERROR):
        ok = check_directory_health(link, repo)

    assert not ok
    assert any("is a symlink" in message for message in caplog.messages)


def test_check_directory_health_rejects_outside_path(
    repo: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Paths escaping the repository root are invalid."""

    outside = repo.parent / "outside"
    with caplog.at_level(logging.ERROR):
        ok = check_directory_health(outside, repo)

    assert not ok
    assert any("escapes repository root" in message for message in caplog.messages)


def test_check_directory_health_non_writable(
    repo: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Non-writable directories should return ``False``."""

    dir_path = repo / "subdir"
    monkeypatch.setattr(os, "access", lambda path, mode: False)

    with caplog.at_level(logging.ERROR):
        ok = check_directory_health(dir_path, repo)

    assert not ok
    assert any("not writable" in message for message in caplog.messages)


def test_check_directory_health_rejects_file(
    repo: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Existing files should be treated as invalid directories."""

    file_path = repo / "codex_sessions"
    file_path.write_text("not a directory", encoding="utf-8")

    with caplog.at_level(logging.ERROR):
        ok = check_directory_health(file_path, repo)

    assert not ok
    assert any("Failed to create" in message for message in caplog.messages)


def test_recover_latest_session_no_archives(
    repo: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Recovering with no archives should return ``None`` and warn."""

    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()
    (repo / LfsPolicy.DEFAULT_SESSION_DIR).mkdir()

    with caplog.at_level(logging.WARNING):
        result = recover_latest_session(tmp_dir, repo, LfsPolicy(repo))

    assert result is None
    assert any("No session archives" in m for m in caplog.messages)


def test_recover_latest_session_invalid_directory(
    repo: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Recovering should fail gracefully when sessions dir is invalid."""

    tmp_dir = repo / "tmp"
    tmp_dir.mkdir()

    bad_dir = repo / LfsPolicy.DEFAULT_SESSION_DIR
    bad_dir.write_text("not a directory", encoding="utf-8")

    with caplog.at_level(logging.ERROR):
        result = recover_latest_session(tmp_dir, repo, LfsPolicy(repo))

    assert result is None
    assert any("Failed to create" in m for m in caplog.messages)

