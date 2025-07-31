#!/usr/bin/env python3
"""Safely commit staged files with Git LFS auto-tracking."""
from __future__ import annotations

import mimetypes
import os
import subprocess
import sys
from pathlib import Path

SIZE_LIMIT = 50 * 1024 * 1024  # 50MB
ALLOW_AUTOLFS = os.getenv("ALLOW_AUTOLFS") == "1"


def run(cmd: str) -> subprocess.CompletedProcess[str]:
    """Run shell command and return CompletedProcess."""
    return subprocess.run(cmd, shell=True, text=True, capture_output=True, check=False)


def staged_files() -> list[str]:
    """Return list of staged files added or modified."""
    res = run("git diff --cached --name-only --diff-filter=ACM")
    return [f for f in res.stdout.splitlines() if f]


def is_binary(path: Path) -> bool:
    """Detect if file is binary using mimetypes and git diff."""
    mime, _ = mimetypes.guess_type(path.as_posix())
    if mime:
        return not mime.startswith("text")
    diff = run(f"git diff --numstat \"{path}\"")
    return diff.stdout.startswith("-\t")


def exceeds_size(path: Path) -> bool:
    """Return True if file exceeds SIZE_LIMIT."""
    try:
        return path.stat().st_size > SIZE_LIMIT
    except OSError:
        return False


def in_gitattributes(path: Path) -> bool:
    """Check if file is already tracked with Git LFS."""
    res = run(f"git check-attr filter -- {path}")
    return res.stdout.strip().endswith("lfs")


def track_extension(ext: str) -> None:
    """Install and track Git LFS for the given extension."""
    run("git lfs install")
    run(f'git lfs track "*{ext}"')
    run("git add .gitattributes")
    print(f"[LFS] Tracking *{ext}")


def process_file(path: Path) -> None:
    """Handle a single staged file."""
    if (is_binary(path) or exceeds_size(path)) and not in_gitattributes(path):
        if ALLOW_AUTOLFS:
            track_extension(path.suffix)
            run(f'git add "{path}"')
        else:
            print(f"Binary or large file detected: {path}. Set ALLOW_AUTOLFS=1 to auto-fix.")
            sys.exit(1)


def main(args: list[str]) -> None:
    for name in staged_files():
        p = Path(name)
        if p.exists():
            process_file(p)
    message = args[0] if args else "auto commit"
    run(f'git commit -m "{message}"')
    if len(args) > 1 and args[1] == "--push":
        run("git push")
    print("✅ Commit successful.")


if __name__ == "__main__":
    main(sys.argv[1:])
