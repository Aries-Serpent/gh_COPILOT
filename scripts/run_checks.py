"""Run linting and tests sequentially."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.validation_utils import anti_recursion_guard
from scripts.run_tests_safe import (
    _write_coverage_absence_log,
    check_pytest_cov_available,
)


def ensure_codex_log_tracked() -> None:
    """Ensure ``codex_log.db`` is tracked by Git LFS."""
    result = subprocess.run(
        ["git", "lfs", "ls-files"],
        capture_output=True,
        text=True,
        check=False,
    )
    tracked = any(line.rstrip().endswith(" codex_log.db") for line in result.stdout.splitlines())
    if result.returncode != 0 or not tracked:
        msg = "codex_log.db must be managed by Git LFS"
        raise RuntimeError(msg)


@anti_recursion_guard
def main() -> int:
    """Run ``ruff`` and ``pytest`` sequentially.

    Returns the exit code of the first failing command, or ``0`` if both
    commands succeed.
    """

    ensure_codex_log_tracked()

    pytest_cmd = ["pytest", "-q"]
    if check_pytest_cov_available():
        pytest_cmd[1:1] = [
            "--cov=scripts.run_migrations",
            "--cov=utils.cross_platform_paths",
            "--cov=scripts.database.unified_database_management_system",
            "--cov=validation.core.rules",
            "--cov-report=term",
            "--cov-fail-under=95",
        ]
    else:
        # Remove any coverage options from environment when plugin is missing
        addopts = os.environ.get("PYTEST_ADDOPTS", "").split()
        addopts = [opt for opt in addopts if not opt.startswith("--cov")]
        os.environ["PYTEST_ADDOPTS"] = " ".join(addopts)
        _write_coverage_absence_log()

    commands = [
        [
            "ruff",
            "check",
            ".",
            "--config",
            str(ROOT / "pyproject.toml"),
            "--force-exclude",
        ],
        ["pyright"],
        pytest_cmd,
    ]

    for cmd in commands:
        result = subprocess.run(cmd, cwd=ROOT)
        if result.returncode != 0:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

