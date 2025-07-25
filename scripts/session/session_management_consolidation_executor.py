"""CLI wrapper for :class:`EnterpriseUtility` from :mod:`session_management_consolidation_executor`."""
from session_management_consolidation_executor import EnterpriseUtility

__all__ = ["EnterpriseUtility", "main"]

def main() -> int:
    """Run :func:`EnterpriseUtility.execute_utility` as CLI."""
    util = EnterpriseUtility()
    return 0 if util.execute_utility() else 1

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
