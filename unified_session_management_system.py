"""Command line wrapper for unified session management."""

from contextlib import contextmanager
from pathlib import Path

from scripts.utilities.unified_session_management_system import (
    UnifiedSessionManagementSystem,
)
from utils.validation_utils import detect_zero_byte_files

__all__ = [
    "UnifiedSessionManagementSystem",
    "ensure_no_zero_byte_files",
    "main",
]


@contextmanager
def ensure_no_zero_byte_files(path: Path) -> None:
    """Ensure ``path`` contains no zero-byte files before and after the block."""
    zero_files = detect_zero_byte_files(path)
    if zero_files:
        raise RuntimeError(f"Zero-byte files detected: {zero_files}")
    yield
    zero_files = detect_zero_byte_files(path)
    if zero_files:
        raise RuntimeError(f"Zero-byte files detected: {zero_files}")


def main() -> int:
    """Run session validation and return an exit code."""
    system = UnifiedSessionManagementSystem()
    success = system.start_session()
    with ensure_no_zero_byte_files(system.workspace_root):
        system.end_session()
    print("Valid" if success else "Invalid")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
