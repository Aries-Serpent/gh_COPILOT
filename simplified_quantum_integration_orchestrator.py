"""Thin wrapper for :mod:`session_management_consolidation_executor`."""

from session_management_consolidation_executor import EnterpriseUtility
from utils.log_utils import _log_plain
from enterprise_modules.compliance import pid_recursion_guard

__all__ = ["EnterpriseUtility", "hello_world"]


@pid_recursion_guard
def hello_world() -> None:
    """Print a friendly greeting."""

    _log_plain("Hello, world!")


if __name__ == "__main__":
    hello_world()
