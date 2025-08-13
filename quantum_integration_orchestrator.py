"""Command-line entry for the quantum integration orchestrator."""

from __future__ import annotations

import argparse
import os
import sys

from enterprise_modules.compliance import pid_recursion_guard
from scripts.automation.quantum_integration_orchestrator import EnterpriseUtility


@pid_recursion_guard
def main(argv: list[str] | None = None) -> int:
    """Run the orchestrator selecting provider backends."""
    parser = argparse.ArgumentParser(description="Quantum Integration Orchestrator")
    parser.add_argument(
        "--provider",
        choices=["simulator", "ibm", "ionq", "dwave"],
        default="simulator",
        help="Quantum provider to use",
    )
    args = parser.parse_args(argv)

    from quantum.providers import get_provider

    provider = get_provider(args.provider)
    token_env = {
        "ibm": "QISKIT_IBM_TOKEN",
        "ionq": "IONQ_API_KEY",
        "dwave": "DWAVE_API_TOKEN",
    }
    if args.provider != "simulator":
        env = token_env[args.provider]
        if not os.getenv(env):
            parser.error(f"--provider {args.provider} requires {env} to be set")

    backend = provider.get_backend()
    util = EnterpriseUtility(backend=backend)
    success = util.execute_utility()
    return 0 if success else 1


__all__ = ["EnterpriseUtility", "main"]


if __name__ == "__main__":
    sys.exit(main())
