import argparse
import os

from quantum.orchestration.executor import QuantumExecutor


def main() -> None:
    parser = argparse.ArgumentParser(description="Quantum Executor CLI")
    parser.add_argument("--use-hardware", action="store_true", help="Use IBM Quantum hardware")
    parser.add_argument(
        "--backend",
        default=os.getenv("IBM_BACKEND", "ibmq_qasm_simulator"),
        help="Backend name",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("QISKIT_IBM_TOKEN"),
        help="IBM Quantum API token",
    )
    args = parser.parse_args()

    if args.token:
        os.environ["QISKIT_IBM_TOKEN"] = args.token
    if args.backend:
        os.environ["IBM_BACKEND"] = args.backend

    executor = QuantumExecutor(
        use_hardware=args.use_hardware, backend_name=args.backend
    )
    if args.use_hardware and not executor.use_hardware:
        print("Hardware backend requested but unavailable; using simulator")
    print(
        f"Backend: {getattr(executor.backend, 'name', 'none')} (hardware={executor.use_hardware})"
    )


if __name__ == "__main__":
    main()
