"""Utility for configuring IBM Quantum tokens and validating backends."""

from __future__ import annotations

import argparse
import os

import json

from quantum.ibm_backend import CONFIG_PATH, init_ibm_backend


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
    parser.add_argument(
        "--save",
        action="store_true",
        help="Persist token to config/qiskit.json for future sessions",
    )
    args = parser.parse_args()

    if args.token:
        os.environ["QISKIT_IBM_TOKEN"] = args.token
        if args.save:
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            CONFIG_PATH.write_text(json.dumps({"QISKIT_IBM_TOKEN": args.token}))
            CONFIG_PATH.chmod(0o600)

    try:
        backend, use_hw = init_ibm_backend(
            token=args.token,
            backend_name=args.backend if args.use_hardware else None,
            enforce_hardware=args.use_hardware,
        )
    except RuntimeError as exc:
        print(f"Error: {exc}")
        return

    if backend is None:
        print("No backend available")
        return

    backend_name = getattr(backend, "name", "unknown")
    print(f"Loaded backend: {backend_name}")
    if use_hw:
        print("Hardware access verified")
    else:
        print("Using simulator backend")


if __name__ == "__main__":
    main()

