#!/usr/bin/env python3
"""Check requirements.txt for duplicate packages.

This utility scans the project's top-level ``requirements.txt`` file and
reports any packages that appear more than once, ignoring case. It exits with
status code 1 if duplicates are found so it can be used in CI or pre-commit
hooks.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path


REQ_FILE = Path(__file__).resolve().parent.parent / "requirements.txt"


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


def main() -> int:
    lines = REQ_FILE.read_text().splitlines()
    counter = Counter(filter(None, (_package_name(l) for l in lines)))
    duplicates = {name: count for name, count in counter.items() if count > 1}

    if duplicates:
        for name, count in duplicates.items():
            print(f"duplicate package: {name} appears {count} times")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

