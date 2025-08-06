#!/usr/bin/env python3
"""Simple roadmap validator.

Checks that each bullet in a roadmap markdown file contains either a link or a
status marker like ``[status: value]``.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

STATUS_PATTERN = re.compile(r"\[status:.*?\]", re.IGNORECASE)


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if line.startswith("-") and not ("http" in line or STATUS_PATTERN.search(line)):
            errors.append(f"{path}:{lineno} missing issue link or status")
    return errors


def main() -> int:
    paths = [Path(p) for p in sys.argv[1:]]
    all_errors: list[str] = []
    for p in paths:
        all_errors.extend(validate_file(p))
    if all_errors:
        print("\n".join(all_errors))
        return 1
    print("All roadmap items validated.")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
