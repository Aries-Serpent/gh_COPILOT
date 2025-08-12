#!/usr/bin/env python3
"""Run a simple circuit on IBM Quantum hardware if available."""

from qiskit import QuantumCircuit

from ghc_quantum.ibm_backend import init_ibm_backend


def main() -> None:
    backend, use_hardware = init_ibm_backend()
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
