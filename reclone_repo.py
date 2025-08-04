#!/usr/bin/env python3
"""Utility to obtain a clean clone of a Git repository.

This script replaces a possibly corrupted working copy by cloning a fresh
copy of a repository. It can optionally back up or remove an existing
destination before cloning.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def ensure_git_available() -> None:
    """Ensure that the ``git`` executable is available."""

    if shutil.which("git") is None:
        raise RuntimeError("git is required but was not found in PATH")


def validate_dest_parent(dest: Path) -> None:
    """Verify that the destination's parent directory exists."""

    if not dest.parent.exists():
        raise RuntimeError(
            f"Destination parent directory does not exist: {dest.parent}"
        )


def validate_backup_root(dest: Path, backup_root: Path) -> None:
    """Validate backup root for ``--backup-existing`` option.

    The backup root must exist and reside outside the destination path to
    avoid recursive moves.
    """

    if not backup_root.exists():
        raise RuntimeError(f"Backup root does not exist: {backup_root}")

    dest_abs = dest.resolve()
    backup_abs = backup_root.resolve()

    if backup_abs == dest_abs or backup_abs in dest_abs.parents:
        raise RuntimeError("Backup root must be outside destination path")
    if dest_abs == backup_abs or dest_abs in backup_abs.parents:
        raise RuntimeError("Destination must be outside backup root")


def backup_existing(dest: Path, backup_root: Path) -> None:
    """Move existing destination directory to a timestamped backup."""

    if not dest.exists():
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_root / f"{dest.name}_{timestamp}"
    shutil.move(str(dest), str(backup_path))


def clean_existing(dest: Path) -> None:
    """Remove the destination directory if it exists."""

    if dest.exists():
        shutil.rmtree(dest)


def git_clone(repo_url: str, branch: str, dest: Path) -> None:
    """Clone the repository using ``git``."""

    cmd = ["git", "clone", "--branch", branch, repo_url, str(dest)]
    subprocess.run(cmd, check=True)


def latest_commit(dest: Path) -> str:
    """Return the latest commit hash in the clone."""

    cmd = ["git", "-C", str(dest), "rev-parse", "HEAD"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description="Re-clone a Git repository")
    parser.add_argument("--repo-url", required=True, help="URL of repository to clone")
    parser.add_argument("--dest", required=True, help="Destination directory")
    parser.add_argument(
        "--branch", default="main", help="Branch or tag to checkout (default: main)"
    )
    parser.add_argument(
        "--backup-existing",
        action="store_true",
        help="Backup the existing destination directory before cloning",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove the destination directory before cloning",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Program entry point."""

    args = parse_args(argv or sys.argv[1:])
    dest = Path(args.dest).expanduser()

    try:
        ensure_git_available()
        validate_dest_parent(dest)

        if args.backup_existing and args.clean:
            print(
                "Cannot use --backup-existing and --clean together",
                file=sys.stderr,
            )
            return 1

        if args.backup_existing:
            backup_root_env = os.environ.get("GH_COPILOT_BACKUP_ROOT")
            if not backup_root_env:
                print(
                    "GH_COPILOT_BACKUP_ROOT environment variable is required for --backup-existing",
                    file=sys.stderr,
                )
                return 1
            backup_root = Path(backup_root_env).expanduser()
            validate_backup_root(dest, backup_root)
            backup_existing(dest, backup_root)
        elif args.clean:
            clean_existing(dest)

        git_clone(args.repo_url, args.branch, dest)
        commit_hash = latest_commit(dest)
        print(commit_hash)
        return 0
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())

