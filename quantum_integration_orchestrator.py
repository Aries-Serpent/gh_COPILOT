"""Thin wrapper for :mod:"scripts.automation.quantum_integration_orchestrator"."""

from scripts.automation.quantum_integration_orchestrator import (
    EnterpriseUtility,
    main as _main,
)


def main() -> None:
    """Entry point forwarding to :mod:`scripts.automation.quantum_integration_orchestrator`."""
    _main()


__all__ = ["EnterpriseUtility", "main"]

if __name__ == "__main__":
    main()
