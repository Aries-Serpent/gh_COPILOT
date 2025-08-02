"""Thin wrapper for :mod:`scripts.session.session_management_consolidation_executor`."""

from scripts.session.session_management_consolidation_executor import EnterpriseUtility
from utils.log_utils import _log_plain

__all__ = ["EnterpriseUtility", "hello_world"]


def hello_world() -> None:
    """Print a friendly greeting."""

    _log_plain("Hello, world!")


if __name__ == "__main__":
    hello_world()
