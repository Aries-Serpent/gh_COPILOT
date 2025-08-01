"""Tests for :meth:`artifact_manager.LfsPolicy.sync_gitattributes`.

These integration tests operate on isolated git repositories provided by the
``git_repo`` fixture.  Each test verifies that ``.gitattributes`` is generated
or updated according to the repository's policy file.
"""

from __future__ import annotations

import logging
from pathlib import Path

from artifact_manager import LfsPolicy


def run_sync(repo: Path) -> None:
    """Helper that executes ``LfsPolicy.sync_gitattributes`` with logging."""

    policy = LfsPolicy(repo)
    logging.info("Synchronizing .gitattributes in %s", repo)
    policy.sync_gitattributes()


def test_gitattributes_created(git_repo: Path, policy_file) -> None:
    """A new policy results in a generated ``.gitattributes`` file."""

    policy_file(
        "gitattributes_template: |\n  *.dat filter=lfs diff=lfs merge=lfs -text\n"
    )
    run_sync(git_repo)
    gitattributes = git_repo / ".gitattributes"
    assert gitattributes.exists()
    content = gitattributes.read_text(encoding="utf-8")
    assert "*.dat" in content


def test_sync_updates_with_new_extension(git_repo: Path, policy_file) -> None:
    """Running sync again incorporates new extensions from policy."""

    policy_file(
        "gitattributes_template: |\n  *.dat filter=lfs diff=lfs merge+lfs -text\n"
    )
    run_sync(git_repo)
    policy_file(
        "gitattributes_template: |\n  *.dat filter=lfs diff=lfs merge+lfs -text\n"
        "binary_extensions:\n  - .dat\n  - .bin\n"
    )
    run_sync(git_repo)
    content = (git_repo / ".gitattributes").read_text(encoding="utf-8")
    assert "*.bin" in content


def test_sync_uses_session_dir(git_repo: Path, policy_file) -> None:
    """The session directory influences generated paths."""

    policy_file(
        "session_artifact_dir: custom_sessions\n"
        "gitattributes_template: |\n  *.zip filter=lfs diff=lfs merge+lfs -text\n"
    )
    run_sync(git_repo)
    content = (git_repo / ".gitattributes").read_text(encoding="utf-8")
    assert "custom_sessions/*.zip" in content


def test_sync_preserves_unrelated_lines(git_repo: Path, policy_file) -> None:
    """Existing ``.gitattributes`` entries remain after synchronization."""

    (git_repo / ".gitattributes").write_text("docs/*.md text\n", encoding="utf-8")
    policy_file(
        "gitattributes_template: |\n  *.dat filter=lfs diff=lfs merge+lfs -text\n"
    )
    run_sync(git_repo)
    content = (git_repo / ".gitattributes").read_text(encoding="utf-8")
    assert content.startswith("# Git LFS rules"), content
    assert "*.dat filter" in content

