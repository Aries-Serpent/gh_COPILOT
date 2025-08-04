"""Utility to obtain a fresh clone of a Git repository.

This script is intended for disaster recovery or when a corrupted working
copy needs to be replaced with a clean clone. It supports backing up or
removing an existing destination before cloning and confirms success by
printing the latest commit hash.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns
    -------
    argparse.Namespace
        Populated namespace with arguments for the cloning operation.
    """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-url",
        required=True,
        help="HTTPS or SSH URL of the Git repository to clone",
    )
    parser.add_argument(
        "--dest",
        required=True,
        help="Destination directory where the new clone will reside",
    )
    parser.add_argument(
        "--branch",
        default="main",
        help="Branch or tag to check out after cloning (default: main)",
    )
    parser.add_argument(
        "--backup-existing",
        action="store_true",
        help=(
            "If set and destination exists, move it to a timestamped backup "
            "under GH_COPILOT_BACKUP_ROOT"
        ),
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove any existing destination directory before cloning",
    )
    return parser.parse_args()


def ensure_git_available() -> None:
    """Ensure the git executable is available on PATH."""

    if shutil.which("git") is None:
        print("Error: git command not found. Please install Git.", file=sys.stderr)
        raise SystemExit(1)


def validate_paths(dest: Path, backup_flag: bool) -> Path | None:
    """Validate destination and backup paths.

    Parameters
    ----------
    dest:
        Destination directory for the clone.
    backup_flag:
        Whether the backup option was requested.

    Returns
    -------
    Path | None
        Resolved path to GH_COPILOT_BACKUP_ROOT when backup_flag is True,
        otherwise None.
    """

    dest_parent = dest.parent
    if not dest_parent.exists():
        print(
            f"Error: parent directory '{dest_parent}' does not exist.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    backup_root = None
    if backup_flag:
        env_var = os.getenv("GH_COPILOT_BACKUP_ROOT")
        if not env_var:
            print(
                "Error: GH_COPILOT_BACKUP_ROOT is not set while --backup-existing is used.",
                file=sys.stderr,
            )
            raise SystemExit(1)
        backup_root = Path(env_var).expanduser().resolve()
        if not backup_root.exists():
            print(
                f"Error: backup root '{backup_root}' does not exist.",
                file=sys.stderr,
            )
            raise SystemExit(1)
        dest_resolved = dest.resolve()
        if backup_root.is_relative_to(dest_resolved):
            print(
                "Error: GH_COPILOT_BACKUP_ROOT cannot be within destination path.",
                file=sys.stderr,
            )
            raise SystemExit(1)

    return backup_root


def backup_existing(dest: Path, backup_root: Path) -> None:
    """Move existing destination to a timestamped backup directory."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{dest.name}_{timestamp}"
    target = backup_root / backup_name
    shutil.move(str(dest), str(target))
    print(f"Existing directory moved to backup: {target}")


def clean_existing(dest: Path) -> None:
    """Remove existing destination directory."""

    shutil.rmtree(dest)
    print(f"Removed existing directory: {dest}")


def clone_repository(repo_url: str, branch: str, dest: Path) -> None:
    """Clone the repository to the destination path."""

    cmd = ["git", "clone", "--branch", branch, repo_url, str(dest)]
    subprocess.check_call(cmd)


def print_latest_commit(dest: Path) -> None:
    """Print the latest commit hash of the cloned repository."""

    cmd = ["git", "-C", str(dest), "rev-parse", "HEAD"]
    result = subprocess.check_output(cmd, text=True).strip()
    print(result)


def main() -> None:
    """Entry point for command-line execution."""

    args = parse_args()
    if args.backup_existing and args.clean:
        print(
            "Error: --backup-existing and --clean are mutually exclusive.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    ensure_git_available()
    dest = Path(args.dest).expanduser()
    backup_root = validate_paths(dest, args.backup_existing)

    if dest.exists():
        if args.backup_existing:
            backup_existing(dest, backup_root)  # type: ignore[arg-type]
        elif args.clean:
            clean_existing(dest)
        else:
            print(
                f"Error: destination '{dest}' already exists. Use --clean or --backup-existing.",
                file=sys.stderr,
            )
            raise SystemExit(1)

    try:
        clone_repository(args.repo_url, args.branch, dest)
        print_latest_commit(dest)
    except subprocess.CalledProcessError as exc:
        print(f"Error: git command failed with exit code {exc.returncode}", file=sys.stderr)
        raise SystemExit(exc.returncode)


if __name__ == "__main__":
    main()
