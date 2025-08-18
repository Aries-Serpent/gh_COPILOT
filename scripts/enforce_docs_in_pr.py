#!/usr/bin/env python3
"""Fail if code changes lack accompanying documentation updates."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


CODE_PREFIXES = ("src/", "scripts/")
DOC_PREFIXES = ("docs/", "documentation/")
DOC_FILES = {"README.md", "README.rst"}


def changed_files(base_ref: str) -> list[str]:
    """Return files changed compared to ``base_ref``."""
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Enforce docs-in-PR policy")
    parser.add_argument(
        "--base",
        default="origin/main",
        help="Base ref for comparison",
    )
    args = parser.parse_args(argv)

    files = changed_files(args.base)
    code_changes = [f for f in files if f.startswith(CODE_PREFIXES) and f.endswith(".py")]
    doc_changes = [
        f for f in files if f.startswith(DOC_PREFIXES) or Path(f).name in DOC_FILES
    ]

    if code_changes and not doc_changes:
        print("Code changes detected without documentation updates:")
        for f in code_changes:
            print(f" - {f}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

