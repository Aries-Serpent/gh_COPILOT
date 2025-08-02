#!/usr/bin/env python3
"""CLI wrapper for :class:`EnterpriseUtility` consolidation executor."""

from session_management_consolidation_executor import EnterpriseUtility

__all__ = ["EnterpriseUtility"]

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(EnterpriseUtility().execute_utility())
