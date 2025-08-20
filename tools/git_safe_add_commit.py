#!/usr/bin/env python3
"""Safely commit staged files with optional Git LFS tracking.

Usage:
    tools/git_safe_add_commit.py MESSAGE [--push]
    tools/git_safe_add_commit.py -h | --help

The script scans staged files and, when ``ALLOW_AUTOLFS=1`` is set, automatically
tracks binary or large files with Git LFS according to ``.codex_lfs_policy.yaml``.
The optional ``--push`` flag pushes the commit to the current remote.
"""

from __future__ import annotations

import mimetypes
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List
import argparse

try:  # pragma: no cover - optional dependency
    import yaml  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise ImportError("PyYAML is required for git_safe_add_commit. Install PyYAML to proceed.") from exc

POLICY_FILE = Path(".codex_lfs_policy.yaml")
SIZE_LIMIT = 50 * 1024 * 1024
BINARY_EXTS = {".db", ".7z", ".zip", ".bak", ".dot", ".sqlite", ".exe"}
GOVERNANCE_DOC = Path("docs/GOVERNANCE_STANDARDS.md")


def _run(cmd: Iterable[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=False, text=True, capture_output=True)


def _load_policy() -> None:
    global SIZE_LIMIT, BINARY_EXTS
    if POLICY_FILE.exists() and yaml:
        data = yaml.safe_load(POLICY_FILE.read_text(encoding="utf-8")) or {}
        SIZE_LIMIT = int(data.get("size_threshold_mb", 50)) * 1024 * 1024
        exts = data.get("binary_extensions")
        if isinstance(exts, list):
            BINARY_EXTS.update({e if e.startswith(".") else f".{e}" for e in exts})


def _staged_files() -> List[str]:
    res = _run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"])
    return [f for f in res.stdout.splitlines() if f]


def _is_binary(path: Path) -> bool:
    if path.suffix.lower() in BINARY_EXTS:
        return True
    mime, _ = mimetypes.guess_type(str(path))
    if mime is not None:
        return not mime.startswith("text")
    try:
        with path.open("rb") as fh:
            chunk = fh.read(1024)
            return b"\0" in chunk
    except OSError:
        return False


def _tracked(path: Path) -> bool:
    if not Path(".gitattributes").exists():
        return False
    pattern = f"*{path.suffix}"
    for line in Path(".gitattributes").read_text(encoding="utf-8").splitlines():
        if line.strip().startswith(pattern) and "filter=lfs" in line:
            return True
    return False


def _track_lfs(ext: str) -> None:
    _run(["git", "lfs", "install"])
    _run(["git", "lfs", "track", f"*{ext}"])
    _run(["git", "add", ".gitattributes"])
    print(f"[LFS] Tracking *{ext}")


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Safely commit staged files and optionally push. Binary or large files "
            "are auto-tracked with Git LFS when ALLOW_AUTOLFS=1. Policy is read from "
            ".codex_lfs_policy.yaml."
        )
    )
    parser.add_argument("message", help="commit message")
    parser.add_argument(
        "--push",
        action="store_true",
        help="push to current remote after committing",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    _load_policy()
    if not GOVERNANCE_DOC.exists():
        print("Missing governance standards document: docs/GOVERNANCE_STANDARDS.md")
        return 1
    if Path("databases/codex_log.db").exists():
        _run(["git", "add", "databases/codex_log.db"])
    files = _staged_files()
    session_db = "databases/codex_session_logs.db"
    if session_db not in files and Path(session_db).exists():
        _run(["git", "add", session_db])
        files = _staged_files()
    allow = os.getenv("ALLOW_AUTOLFS") == "1"
    for f in files:
        path = Path(f)
        if not path.exists():
            continue
        size = path.stat().st_size
        if (_is_binary(path) or size > SIZE_LIMIT) and not _tracked(path):
            if allow:
                _track_lfs(path.suffix)
                _run(["git", "add", str(path)])
            else:
                print(f"Binary or large file detected: {path}. Set ALLOW_AUTOLFS=1 to auto-track.")
                return 1
    commit = _run(["git", "commit", "-m", args.message])
    if commit.returncode != 0:
        sys.stdout.write(commit.stdout)
        sys.stderr.write(commit.stderr)
        return commit.returncode
    if args.push:
        push = _run(["git", "push"])
        sys.stdout.write(push.stdout)
        sys.stderr.write(push.stderr)
    print("\N{CHECK MARK} Commit successful.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
