#!/usr/bin/env python3
"""Check requirements files for duplicate packages.

This utility scans one or more ``requirements`` files and reports any packages
that appear more than once within each file (case-insensitive). It exits with
status code ``1`` if duplicates are found so it can be used in CI, pre-commit
hooks, or Makefile targets.
"""

from __future__ import annotations

import re
import sys
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path


def _package_name(line: str) -> str | None:
    """Extract the package name from a requirements line.

    Comments and environment markers are ignored. Returns ``None`` for empty
    or comment-only lines.
    """

    line = line.split("#", 1)[0].strip()
    if not line:
        return None

    # Drop environment markers such as ``; sys_platform == 'win32'``
    line = line.split(";", 1)[0]

    match = re.match(r"([A-Za-z0-9._-]+)", line)
    return match.group(1).lower() if match else None

def _find_duplicates(path: Path) -> dict[str, int]:
    """Return a mapping of duplicate package names to occurrence counts."""

    lines = path.read_text().splitlines()
    counter = Counter(filter(None, (_package_name(l) for l in lines)))
    return {name: count for name, count in counter.items() if count > 1}


def main(argv: list[str] | None = None) -> int:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "files",
        nargs="*",
        default=["requirements.txt"],
        help="requirements files to scan",
    )
    args = parser.parse_args(argv)

    had_duplicates = False
    for file_name in args.files:
        path = Path(file_name)
        duplicates = _find_duplicates(path)
        for name, count in duplicates.items():
            print(f"{path}: duplicate package '{name}' appears {count} times")
        had_duplicates |= bool(duplicates)

    return 1 if had_duplicates else 0


if __name__ == "__main__":
    sys.exit(main())

