"""Command line wrapper for unified session management."""

from scripts.utilities.unified_session_management_system import (
    UnifiedSessionManagementSystem,
)

__all__ = ["UnifiedSessionManagementSystem", "main"]


def main() -> int:
    """Run session validation and return an exit code."""
    system = UnifiedSessionManagementSystem()
    success = system.start_session()
    print("Valid" if success else "Invalid")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
