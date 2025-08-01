"""Tests for automatic Git LFS tracking in ``git_safe_add_commit.py``."""

from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path


SCRIPT = Path("tools/git_safe_add_commit.py").resolve()


def test_autolfs_enabled(git_repo: Path) -> None:
    """Binary files trigger automatic LFS tracking when enabled."""

    bin_file = git_repo / "data.bin"
    logging.info("Creating %s", bin_file)
    bin_file.write_bytes(b"\x00\x01\x02")
    subprocess.run(["git", "add", str(bin_file)], cwd=git_repo, check=True)

    env = os.environ.copy()
    env["ALLOW_AUTOLFS"] = "1"
    env["PYTHONPATH"] = str(Path.cwd())
    proc = subprocess.run(
        ["python", str(SCRIPT), "test"],
        cwd=git_repo,
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert "[LFS] Tracking *.bin" in proc.stdout
    assert "*.bin" in (git_repo / ".gitattributes").read_text(encoding="utf-8")


def test_autolfs_disabled(git_repo: Path) -> None:
    """Without ``ALLOW_AUTOLFS``, binary files cause the script to fail."""

    bin_file = git_repo / "data.bin"
    logging.info("Creating %s", bin_file)
    bin_file.write_bytes(b"\x00\x01\x02")
    subprocess.run(["git", "add", str(bin_file)], cwd=git_repo, check=True)

    env = os.environ.copy()
    env.pop("ALLOW_AUTOLFS", None)
    env["PYTHONPATH"] = str(Path.cwd())
    proc = subprocess.run(
        ["python", str(SCRIPT), "test"],
        cwd=git_repo,
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    assert "Binary or large file detected" in proc.stdout
    assert not (git_repo / ".gitattributes").exists()

