# Quantum Hardware Configuration

The quantum modules operate in simulation mode by default. To execute on IBM
Quantum hardware:

1. Install the optional `qiskit-ibm-provider` dependency.
2. Supply your IBM Quantum API token using the `QISKIT_IBM_TOKEN` environment
   variable or the `--token` flag of `quantum/cli/executor_cli.py`.
3. Select a backend with the `IBM_BACKEND` environment variable or the
   `--backend` CLI flag. When unspecified, the system auto-selects an available
   backend.
4. Pass `--use-hardware` to the CLI (or equivalent flags in other tools) to
   request hardware execution.

If hardware initialization fails for any reason, the executor transparently
falls back to the local Qiskit simulator.

