"""Command-line entry for the quantum integration orchestrator."""

from __future__ import annotations

import argparse
import os
import sys

from scripts.automation.quantum_integration_orchestrator import EnterpriseUtility


def main(argv: list[str] | None = None) -> int:
    """Run the orchestrator with optional hardware support."""
    parser = argparse.ArgumentParser(description="Quantum Integration Orchestrator")
    parser.add_argument("--hardware", action="store_true", help="Use IBM Quantum hardware backend")
    parser.add_argument(
        "--backend",
        default=os.getenv("IBM_BACKEND", "ibmq_qasm_simulator"),
        help="Backend name to use",
    )
    args = parser.parse_args(argv)

    if args.hardware and not os.getenv("QISKIT_IBM_TOKEN"):
        parser.error("--hardware requires QISKIT_IBM_TOKEN to be set")

    util = EnterpriseUtility(use_hardware=args.hardware, backend_name=args.backend)
    success = util.execute_utility()
    return 0 if success else 1


__all__ = ["EnterpriseUtility", "main"]


if __name__ == "__main__":
    sys.exit(main())
