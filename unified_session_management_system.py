"""Command line wrapper for unified session management."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Callable
import logging

from utils.validation_utils import detect_zero_byte_files, anti_recursion_guard
from enterprise_modules.compliance import validate_environment, ComplianceError

logger = logging.getLogger(__name__)

__all__ = [
    "ensure_no_zero_byte_files",
    "main",
]


@contextmanager
def ensure_no_zero_byte_files(root: str | Path):
    """Verify the workspace is free of zero-byte files before and after the block."""
    root_path = Path(root)
    before = detect_zero_byte_files(root_path)
    if before:
        for path in before:
            path.unlink(missing_ok=True)
        raise RuntimeError(f"Zero-byte files detected: {before}")
    yield
    after = detect_zero_byte_files(root_path)
    if after:
        for path in after:
            path.unlink(missing_ok=True)
        raise RuntimeError(f"Zero-byte files detected: {after}")


def prevent_recursion(func: Callable) -> Callable:
    """Decorator forwarding to :func:`anti_recursion_guard`.

    It raises ``RuntimeError`` when ``func`` is invoked recursively within the
    same process. This lightweight wrapper is re-exported for convenience so
    other modules can apply the guard without importing validation utilities
    directly.
    """

    return anti_recursion_guard(func)


@anti_recursion_guard
def main() -> int:
    """Run session validation and return an exit code."""
    from scripts.utilities.unified_session_management_system import (
        UnifiedSessionManagementSystem,
    )
    try:
        validate_environment()
    except ComplianceError as exc:  # pragma: no cover - simple error log
        logger.error("Environment validation failed: %s", exc)
        print("Invalid")
        return 1

    system = UnifiedSessionManagementSystem()
    logger.info("Lifecycle start")
    success = system.start_session()
    with ensure_no_zero_byte_files(system.workspace_root):
        system.end_session()
    logger.info("Lifecycle end")
    print("Valid" if success else "Invalid")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
