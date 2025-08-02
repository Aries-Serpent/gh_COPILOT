#!/usr/bin/env python3
"""Run a simple circuit on IBM Quantum hardware if available."""

import argparse

from qiskit import QuantumCircuit

from quantum.ibm_backend import init_ibm_backend


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a demo circuit")
    parser.add_argument("--hardware", action="store_true", help="Require hardware backend")
    parser.add_argument("--backend", help="Specific backend name to use")
    args = parser.parse_args()

    backend, use_hardware = init_ibm_backend(
        backend_name=args.backend,
        enforce_hardware=args.hardware,
    )
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)
    if backend is None:
        print("No backend available")
        return
    backend.run(qc).result()
    print(f"use_hardware={use_hardware}")


if __name__ == "__main__":
    main()
