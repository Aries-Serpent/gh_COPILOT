"""Tests for ``reclone_repo.py``."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "reclone_repo.py"


def init_repo(path: Path) -> str:
    """Create a simple git repository and return its commit hash."""

    subprocess.run(["git", "init", "-b", "master", str(path)], check=True)
    readme = path / "README.md"
    readme.write_text("test", encoding="utf-8")
    subprocess.run(["git", "-C", str(path), "add", "README.md"], check=True)
    subprocess.run(["git", "-C", str(path), "commit", "-m", "init"], check=True)
    rev = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return rev.stdout.strip()


def run_script(args: list[str], env: dict[str, str]) -> None:
    """Run the reclone script with the given arguments and environment."""

    cmd = [sys.executable, str(SCRIPT), *args]
    subprocess.run(cmd, check=True, env=env)


def test_backup_existing(tmp_path):
    """Existing destination should be backed up before cloning."""

    src = tmp_path / "src"
    dest = tmp_path / "dest"
    backup_root = tmp_path / "backups"
    backup_root.mkdir()

    expected = init_repo(src)
    dest.mkdir()
    (dest / "old.txt").write_text("old", encoding="utf-8")

    env = os.environ.copy()
    env["GH_COPILOT_BACKUP_ROOT"] = str(backup_root)

    run_script(
        [
            "--repo-url",
            str(src),
            "--dest",
            str(dest),
            "--branch",
            "master",
            "--backup-existing",
        ],
        env,
    )

    rev = subprocess.run(
        ["git", "-C", str(dest), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert rev == expected

    backups = list(backup_root.iterdir())
    assert len(backups) == 1
    assert (backups[0] / "old.txt").exists()


def test_clean(tmp_path):
    """Destination directory should be removed when ``--clean`` is given."""

    src = tmp_path / "src2"
    dest = tmp_path / "dest2"
    expected = init_repo(src)
    dest.mkdir()
    (dest / "junk.txt").write_text("junk", encoding="utf-8")

    env = os.environ.copy()

    run_script(
        [
            "--repo-url",
            str(src),
            "--dest",
            str(dest),
            "--branch",
            "master",
            "--clean",
        ],
        env,
    )

    rev = subprocess.run(
        ["git", "-C", str(dest), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert rev == expected
    assert not (dest / "junk.txt").exists()

