import argparse
import os

from ghc_quantum.orchestration.executor import QuantumExecutor


def main() -> None:
    parser = argparse.ArgumentParser(description="Quantum Executor CLI")
    parser.add_argument("--use-hardware", action="store_true", help="Use IBM Quantum hardware")
    parser.add_argument("--backend", default=os.getenv("IBM_BACKEND", "ibmq_qasm_simulator"), help="Backend name")
    args = parser.parse_args()

    if args.use_hardware and not os.getenv("QISKIT_IBM_TOKEN"):
        parser.error("--use-hardware requires QISKIT_IBM_TOKEN to be set")

    executor = QuantumExecutor(use_hardware=args.use_hardware, backend_name=args.backend)
    print(f"Backend: {getattr(executor.backend, 'name', 'none')}")


if __name__ == "__main__":
    main()
