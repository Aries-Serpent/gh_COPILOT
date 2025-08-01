"""Tests for synchronizing `.gitattributes` using the CLI."""
from __future__ import annotations

import difflib
import subprocess
import sys
from pathlib import Path

import pytest


def _run_cli_sync(repo: Path, script: Path) -> subprocess.CompletedProcess[str]:
    """Execute the artifact manager with ``--sync-gitattributes``."""

    return subprocess.run(
        [sys.executable, str(script), "--sync-gitattributes"],
        cwd=repo,
        text=True,
        capture_output=True,
    )


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_cli_sync_creates_file(git_repo: Path, write_policy, copy_cli: Path, newline: str) -> None:
    """The sync flag should create `.gitattributes` based on policy template."""

    write_policy(
        "gitattributes_template: |\n  *.dat filter=lfs diff=lfs merge=lfs -text\n",
        newline=newline,
    )
    result = _run_cli_sync(git_repo, copy_cli)
    assert result.returncode == 0, result.stderr

    expected = (
        "# Git LFS rules for binary artifacts\n"
        "*.dat filter=lfs diff=lfs merge=lfs -text\n"
        "codex_sessions/*.zip filter=lfs diff=lfs merge=lfs -text\n"
        "*.db filter=lfs diff=lfs merge=lfs -text\n"
        "*.7z filter=lfs diff=lfs merge=lfs -text\n"
        "*.zip filter=lfs diff=lfs merge=lfs -text\n"
        "*.bak filter=lfs diff=lfs merge=lfs -text\n"
        "*.dot filter=lfs diff=lfs merge=lfs -text\n"
        "*.sqlite filter=lfs diff=lfs merge=lfs -text\n"
        "*.exe filter=lfs diff=lfs merge=lfs -text\n"
        "# End of LFS patterns\n"
    )
    content = (git_repo / ".gitattributes").read_text(encoding="utf-8")
    if content.strip() != expected.strip():
        diff = "\n".join(
            difflib.unified_diff(expected.splitlines(), content.splitlines())
        )
        pytest.fail(f".gitattributes mismatch:\n{diff}")


def test_cli_sync_overwrites_custom_entries(
    git_repo: Path, write_policy, copy_cli: Path
) -> None:
    """Existing unrelated entries are replaced by policy output."""

    (git_repo / ".gitattributes").write_text("# custom\n*.txt text\n", encoding="utf-8")
    write_policy(
        "gitattributes_template: |\n  *.zip filter=lfs diff=lfs merge=lfs -text\n",
    )
    result = _run_cli_sync(git_repo, copy_cli)
    assert result.returncode == 0, result.stderr

    expected = (
        "# Git LFS rules for binary artifacts\n"
        "*.zip filter=lfs diff=lfs merge=lfs -text\n"
        "codex_sessions/*.zip filter=lfs diff=lfs merge=lfs -text\n"
        "*.db filter=lfs diff=lfs merge=lfs -text\n"
        "*.7z filter=lfs diff=lfs merge=lfs -text\n"
        "*.bak filter=lfs diff=lfs merge=lfs -text\n"
        "*.dot filter=lfs diff=lfs merge=lfs -text\n"
        "*.sqlite filter=lfs diff=lfs merge=lfs -text\n"
        "*.exe filter=lfs diff=lfs merge=lfs -text\n"
        "# End of LFS patterns\n"
    )
    content = (git_repo / ".gitattributes").read_text(encoding="utf-8")
    assert "# custom" not in content
    if content.strip() != expected.strip():
        diff = "\n".join(
            difflib.unified_diff(expected.splitlines(), content.splitlines())
        )
        pytest.fail(f".gitattributes mismatch:\n{diff}")


def test_cli_sync_updates_on_policy_change(
    git_repo: Path, write_policy, copy_cli: Path
) -> None:
    """Synchronizing twice should pick up new extensions from policy changes."""

    write_policy(
        "gitattributes_template: |\n  *.dat filter=lfs diff=lfs merge=lfs -text\n",
    )
    assert _run_cli_sync(git_repo, copy_cli).returncode == 0

    write_policy(
        "gitattributes_template: |\n  *.dat filter=lfs diff=lfs merge=lfs -text\n"
        "  *.bin filter=lfs diff=lfs merge=lfs -text\n",
    )
    assert _run_cli_sync(git_repo, copy_cli).returncode == 0

    content = (git_repo / ".gitattributes").read_text(encoding="utf-8")
    assert "*.bin" in content


def test_sync_uses_session_dir(git_repo: Path, write_policy, copy_cli: Path) -> None:
    """The session directory from policy should prefix archive patterns."""

    write_policy(
        "session_artifact_dir: custom_sessions\n"
        "gitattributes_template: |\n  *.zip filter=lfs diff=lfs merge=lfs -text\n",
    )
    assert _run_cli_sync(git_repo, copy_cli).returncode == 0
    content = (git_repo / ".gitattributes").read_text(encoding="utf-8")
    assert "custom_sessions/*.zip" in content
