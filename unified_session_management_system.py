"""Command line wrapper for unified session management."""

from __future__ import annotations

from typing import Any, Callable
import functools
import os

from scripts.utilities.unified_session_management_system import (
    UnifiedSessionManagementSystem,
)
from utils.validation_utils import detect_zero_byte_files

__all__ = [
    "UnifiedSessionManagementSystem",
    "ensure_no_zero_byte_files",
    "main",
]


_active_pids: dict[tuple[str, str], set[int]] = {}


def prevent_recursion(func: Callable[..., Any]) -> Callable[..., Any]:
    """Prevent recursive execution of ``func`` within the same process.

    The decorator tracks the process ID (PID) for each decorated function. If the
    function attempts to call itself recursively within the same PID, a
    ``RuntimeError`` is raised to halt execution and avoid infinite loops.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        pid = os.getpid()
        key = (func.__module__, func.__qualname__)
        pids = _active_pids.setdefault(key, set())
        if pid in pids:
            raise RuntimeError("Recursion detected")
        pids.add(pid)
        try:
            return func(*args, **kwargs)
        finally:
            pids.remove(pid)
            if not pids:
                _active_pids.pop(key, None)

    return wrapper


__all__ = ["UnifiedSessionManagementSystem", "main", "prevent_recursion"]


@prevent_recursion
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
