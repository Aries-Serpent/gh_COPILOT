"""Thin wrapper for :mod:`archive.consolidated_scripts.simplified_quantum_integration_orchestrator`."""
from archive.consolidated_scripts.simplified_quantum_integration_orchestrator import (
    EnterpriseUtility,
)

__all__ = ["EnterpriseUtility", "hello_world"]


def hello_world() -> None:
    """Print a friendly greeting."""

    print("Hello, world!")


if __name__ == "__main__":
    hello_world()
