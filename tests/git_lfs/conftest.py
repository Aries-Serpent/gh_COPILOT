"""Shared fixtures for Git LFS-related tests.

These fixtures provide isolated git repositories and helpers for writing
``.codex_lfs_policy.yaml`` files.  Each fixture logs filesystem operations so
tests can verify behavior and future contributors understand preconditions.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path
from zipfile import ZipFile

import pytest


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """Create an empty git repository for integration tests.

    The repository contains a single ``README.md`` commit so subsequent git
    commands succeed.  The fixture returns the repository path.
    """

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, stdout=subprocess.DEVNULL)
    readme = tmp_path / "README.md"
    logging.info("Creating %s", readme)
    readme.write_text("init", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "commit", "-m", "init"], cwd=tmp_path, check=True, stdout=subprocess.DEVNULL
    )
    return tmp_path


@pytest.fixture
def policy_file(git_repo: Path):
    """Return a helper to write a policy file in ``git_repo``.

    Parameters
    ----------
    git_repo:
        Path to the repository created by :func:`git_repo`.

    Returns
    -------
    callable
        ``writer(content: str) -> Path`` that writes ``.codex_lfs_policy.yaml``
        with ``content`` and returns the path.
    """

    def writer(content: str) -> Path:
        path = git_repo / ".codex_lfs_policy.yaml"
        logging.info("Writing policy to %s", path)
        path.write_text(content, encoding="utf-8")
        return path

    return writer


# Artifact collection -----------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def collect_artifacts(tmp_path: Path, request) -> None:
    """Persist per-test files under ``repo/tmp`` for later inspection."""

    yield
    repo_tmp = REPO_ROOT / "tmp" / request.node.name
    repo_tmp.parent.mkdir(parents=True, exist_ok=True)
    if repo_tmp.exists():
        shutil.rmtree(repo_tmp)
    shutil.copytree(tmp_path, repo_tmp)


@pytest.fixture(scope="session", autouse=True)
def zip_repo_tmp() -> None:
    """Zip collected artifacts from Git LFS tests into ``tmp/test_artifacts.zip``."""

    yield
    repo_tmp = REPO_ROOT / "tmp"
    if not repo_tmp.exists():
        return
    zip_path = repo_tmp / "test_artifacts.zip"
    with ZipFile(zip_path, "a") as zf:
        for file in repo_tmp.rglob("*"):
            if file == zip_path:
                continue
            zf.write(file, file.relative_to(repo_tmp))
    for item in repo_tmp.iterdir():
        if item.is_dir():
            shutil.rmtree(item)

