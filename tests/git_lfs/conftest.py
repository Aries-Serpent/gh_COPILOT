"""Fixtures for Git LFS related tests."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest


def _init_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, stdout=subprocess.DEVNULL)
    (path / "README.md").write_text("init", encoding="utf-8")
    docs = path / "docs"
    docs.mkdir()
    (docs / "GOVERNANCE_STANDARDS.md").write_text("rules", encoding="utf-8")
    subprocess.run(
        ["git", "add", "README.md", "docs/GOVERNANCE_STANDARDS.md"],
        cwd=path,
        check=True,
    )
    subprocess.run(["git", "commit", "-m", "init"], cwd=path, check=True, stdout=subprocess.DEVNULL)


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """Create a temporary git repository for LFS tests."""

    _init_repo(tmp_path)
    return tmp_path


@pytest.fixture
def write_policy(git_repo: Path):
    """Return a helper that writes ``.codex_lfs_policy.yaml`` to ``git_repo``."""

    def _write(content: str, newline: str = "\n") -> Path:
        policy = git_repo / ".codex_lfs_policy.yaml"
        policy.write_text(content, encoding="utf-8", newline=newline)
        return policy

    return _write


@pytest.fixture
def copy_cli(git_repo: Path) -> Path:
    """Copy ``artifact_manager.py`` into the git repository for CLI invocation."""

    dst = git_repo / "artifact_manager.py"
    shutil.copy(Path(__file__).resolve().parents[2] / "artifact_manager.py", dst)
    return dst
