"""Utility for configuring IBM Quantum tokens and validating backends."""

from __future__ import annotations

import argparse
import os

from quantum.utils.backend_provider import get_backend


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Configure QISKIT_IBM_TOKEN and validate backend access"
    )
    parser.add_argument("--token", help="IBM Quantum API token")
    parser.add_argument(
        "--backend",
        default=os.getenv("IBM_BACKEND", "ibmq_qasm_simulator"),
        help="Backend name to validate",
    )
    parser.add_argument(
        "--use-hardware",
        action="store_true",
        help="Require hardware backend (fallback to simulator otherwise)",
    )
    args = parser.parse_args()

    if args.token:
        os.environ["QISKIT_IBM_TOKEN"] = args.token

    backend = get_backend(args.backend, use_hardware=args.use_hardware or None)
    if backend is None:
        print("No backend available")
        return

    backend_name = getattr(backend, "name", "unknown")
    print(f"Loaded backend: {backend_name}")
    if args.use_hardware and backend_name == "qasm_simulator":
        print("Hardware backend unavailable; used simulator instead")


if __name__ == "__main__":
    main()

