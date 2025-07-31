#!/usr/bin/env python3
"""Safely commit staged files with optional Git LFS auto-tracking."""

from __future__ import annotations

import mimetypes
import os
import subprocess
import sys
from pathlib import Path

SIZE_LIMIT = 50 * 1024 * 1024  # 50MB
ALLOW_AUTOLFS = os.getenv("ALLOW_AUTOLFS") == "1"


def run(cmd: list[str], cwd: str | None = None) -> subprocess.CompletedProcess[str]:
    """Run command and return completed process."""
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)


def is_binary(path: Path) -> bool:
    """Detect if a file is binary using git diff --numstat or mimetypes."""
    result = run(["git", "diff", "--numstat", str(path)])
    if result.stdout.startswith("-\t"):
        return True
    mime, _ = mimetypes.guess_type(path.name)
    return mime is None or ("text" not in mime and "json" not in mime)


def in_gitattributes(path: Path) -> bool:
    result = run(["git", "check-attr", "filter", "--", str(path)])
    return result.stdout.strip().endswith("lfs")


def track_lfs(pattern: str) -> None:
    run(["git", "lfs", "install"])
    run(["git", "lfs", "track", pattern])
    run(["git", "add", ".gitattributes"])
    print(f"[LFS] Tracking {pattern}")


def main() -> None:
    message = sys.argv[1] if len(sys.argv) > 1 else "auto commit"
    files = run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"]).stdout.splitlines()
    for fname in files:
        path = Path(fname)
        if not path.exists():
            continue
        size = path.stat().st_size
        if (is_binary(path) or size > SIZE_LIMIT) and not in_gitattributes(path):
            if not ALLOW_AUTOLFS:
                print(f"Binary or large file detected: {fname}. Set ALLOW_AUTOLFS=1 to auto-track with git lfs.")
                sys.exit(1)
            ext = path.suffix or os.path.splitext(fname)[1]
            pattern = f"*{ext}"
            track_lfs(pattern)
            run(["git", "add", fname])
    commit = run(["git", "commit", "-m", message])
    if commit.returncode != 0:
        sys.stdout.write(commit.stdout)
        sys.stderr.write(commit.stderr)
        sys.exit(commit.returncode)
    print("✅ Commit successful.")
    if "--push" in sys.argv:
        push = run(["git", "push"])
        sys.stdout.write(push.stdout)
        sys.stderr.write(push.stderr)


if __name__ == "__main__":
    main()
