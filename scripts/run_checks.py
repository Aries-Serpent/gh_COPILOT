"""Run linting and tests sequentially."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.validation_utils import anti_recursion_guard


@anti_recursion_guard
def main() -> int:
    """Run ``ruff`` and ``pytest`` sequentially.

    Returns the exit code of the first failing command, or ``0`` if both
    commands succeed.
    """

    commands = [
        ["ruff", "check", "."],
        ["pytest"],
    ]

    for cmd in commands:
        result = subprocess.run(cmd)
        if result.returncode != 0:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

