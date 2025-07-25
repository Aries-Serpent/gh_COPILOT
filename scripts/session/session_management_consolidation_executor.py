#!/usr/bin/env python3
"""CLI wrapper for :class:`EnterpriseUtility`."""

from session_management_consolidation_executor import EnterpriseUtility


def main() -> int:
    """Run the enterprise utility."""
    return 0 if EnterpriseUtility().execute_utility() else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

