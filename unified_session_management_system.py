"""Command line wrapper for unified session management."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import logging

from scripts.utilities.unified_session_management_system import (
    UnifiedSessionManagementSystem,
)
from utils.validation_utils import detect_zero_byte_files, anti_recursion_guard

logger = logging.getLogger(__name__)

__all__ = [
    "ensure_no_zero_byte_files",
    "prevent_recursion",
    "main",
]


@contextmanager
def ensure_no_zero_byte_files(root: str | Path):
    """Verify the workspace is free of zero-byte files before and after the block."""
    root_path = Path(root)
    before = detect_zero_byte_files(root_path)
    if before:
        raise RuntimeError(f"Zero-byte files detected: {before}")
    yield
    after = detect_zero_byte_files(root_path)
    if after:
        raise RuntimeError(f"Zero-byte files detected: {after}")


@anti_recursion_guard
def main() -> int:
    """Run session validation and return an exit code."""
    from scripts.utilities.unified_session_management_system import (
        UnifiedSessionManagementSystem,
    )

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
