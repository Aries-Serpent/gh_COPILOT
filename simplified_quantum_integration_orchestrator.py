"""Thin wrapper for :mod:`session_management_consolidation_executor`."""
from session_management_consolidation_executor import EnterpriseUtility

__all__ = ["EnterpriseUtility", "hello_world"]


def hello_world() -> None:
    """Print a friendly greeting."""

    print("Hello, world!")


if __name__ == "__main__":
    hello_world()
