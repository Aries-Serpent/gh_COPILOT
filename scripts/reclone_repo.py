#!/usr/bin/env python3
"""Utility for cloning a fresh copy of a Git repository.

This script replaces an existing working directory with a clean clone. It
supports backing up or removing an existing directory before cloning.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-url", required=True, help="HTTPS or SSH URL of the repository to clone")
    parser.add_argument("--dest", required=True, help="Destination directory for the new clone")
    parser.add_argument("--branch", default="main", help="Branch or tag to check out (default: main)")
    parser.add_argument(
        "--backup-existing",
        action="store_true",
        help="Move existing destination to a timestamped backup inside GH_COPILOT_BACKUP_ROOT",
    )
    parser.add_argument(
        "--clean", action="store_true", help="Remove any existing destination directory before cloning"
    )
    return parser.parse_args()


def ensure_git_installed() -> None:
    """Raise an error if git is not available."""
    if shutil.which("git") is None:
        raise RuntimeError("git is not installed or not found in PATH")


def validate_paths(dest: str, backup: bool) -> None:
    """Validate destination and backup settings."""
    dest_abs = os.path.abspath(dest)
    parent = os.path.dirname(dest_abs)
    if not os.path.isdir(parent):
        raise RuntimeError(f"Destination parent '{parent}' does not exist")

    if backup and os.path.exists(dest_abs):
        backup_root = os.environ.get("GH_COPILOT_BACKUP_ROOT")
        if not backup_root:
            raise RuntimeError("GH_COPILOT_BACKUP_ROOT is not set")
        backup_root = os.path.abspath(backup_root)
        if not os.path.isdir(backup_root):
            raise RuntimeError(f"Backup root '{backup_root}' does not exist")
        common = os.path.commonpath([dest_abs, backup_root])
        if common == dest_abs:
            raise RuntimeError("GH_COPILOT_BACKUP_ROOT must be outside the destination path")


def backup_existing(dest: str) -> str:
    """Move the existing destination to the backup root and return the backup path."""
    dest_abs = os.path.abspath(dest)
    backup_root = os.path.abspath(os.environ["GH_COPILOT_BACKUP_ROOT"])
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = os.path.basename(dest_abs.rstrip(os.sep))
    backup_path = os.path.join(backup_root, f"{base}_{timestamp}")
    shutil.move(dest_abs, backup_path)
    return backup_path


def remove_existing(dest: str) -> None:
    """Remove the destination directory if it exists."""
    if os.path.exists(dest):
        shutil.rmtree(dest)


def clone_repository(repo_url: str, dest: str, branch: str) -> str:
    """Clone the repository and return the latest commit hash."""
    subprocess.run(["git", "clone", "--branch", branch, repo_url, dest], check=True)
    result = subprocess.run(
        ["git", "-C", dest, "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def main() -> None:
    args = parse_args()
    try:
        ensure_git_installed()
        if args.backup_existing and args.clean:
            raise RuntimeError("--clean cannot be used with --backup-existing")
        validate_paths(args.dest, args.backup_existing)

        if os.path.exists(args.dest):
            if args.backup_existing:
                backup_existing(args.dest)
            elif args.clean:
                remove_existing(args.dest)
            else:
                raise RuntimeError(
                    f"Destination '{args.dest}' already exists. Use --clean or --backup-existing."
                )

        commit = clone_repository(args.repo_url, args.dest, args.branch)
        print(commit)
    except Exception as exc:  # pragma: no cover - broad exception for CLI user feedback
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
