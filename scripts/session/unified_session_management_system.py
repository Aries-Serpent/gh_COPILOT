"""CLI wrapper for :class:`UnifiedSessionManagementSystem`.

Delegates to :mod:`scripts.utilities.unified_session_management_system` to
avoid code duplication.
"""
from scripts.utilities.unified_session_management_system import (
    UnifiedSessionManagementSystem,
)

__all__ = ["UnifiedSessionManagementSystem", "main"]

def main() -> int:
    """Start a session validation run."""
    system = UnifiedSessionManagementSystem()
    return 0 if system.start_session() else 1

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
