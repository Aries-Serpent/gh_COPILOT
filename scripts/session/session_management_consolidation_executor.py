"""CLI wrapper for :mod:`session_management_consolidation_executor`."""

from session_management_consolidation_executor import EnterpriseUtility, main

__all__ = ["EnterpriseUtility", "main"]


if __name__ == "__main__":
    raise SystemExit(main())

