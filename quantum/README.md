# Quantum Utilities

This package provides experimental quantum-inspired utilities used across the
gh_COPILOT toolkit.

> **Note**
> Modules automatically run on IBM Quantum hardware when `qiskit-ibm-provider`
> is installed and `QISKIT_IBM_TOKEN` is set. Otherwise they fall back to the
> local simulator.

## Optimizers
- `optimizers.quantum_optimizer.QuantumOptimizer` – classical/quantum hybrid
  optimizer with progress logging. Events are recorded using
  `utils.log_utils._log_event` when executed via higher-level workflows.
  Use `configure_backend()` to automatically load IBM Quantum credentials from
  `QISKIT_IBM_TOKEN` and select either hardware or the local simulator.

## Database Search
- `quantum.quantum_database_search` – lightweight helpers for SQL, NoSQL and
  hybrid search. All queries are logged to `analytics.db` for compliance.

## Data Pipelines
- `quantum.quantum_data_pipeline.QuantumDataPipeline` – orchestrates database
  joins and advanced algorithms (Grover search and VQE). Pipelines attempt to
  use IBM Quantum hardware when available and otherwise fall back to the local
  simulator.

These modules default to simulation mode but can use real IBM Quantum hardware
when `qiskit-ibm-provider` is installed and `QISKIT_IBM_TOKEN` is configured.
Use the `--use-hardware` flag in `quantum_integration_orchestrator.py` to force
hardware execution or `--simulator` to force local simulation. When no backend
is specified the orchestrator automatically selects an available device. If
hardware is unavailable, the modules automatically fall back to local
simulation.

Hardware usage can also be toggled globally by setting the environment variable
`QUANTUM_USE_HARDWARE` to `"1"` or `"0"`. If the variable is unset the modules
auto-detect availability based on `QISKIT_IBM_TOKEN`.

## IBM Quantum Access

To run on real IBM Quantum hardware you need an access token from
<https://quantum-computing.ibm.com>. Set the environment variable
`QISKIT_IBM_TOKEN` before executing any demo modules or use the helper
`quantum/cli/token_setup.py` script:

```
export QISKIT_IBM_TOKEN="YOUR_API_TOKEN"
# or
python -m quantum.cli.token_setup --token YOUR_API_TOKEN --use-hardware
```

If the token or requested backend is unavailable the modules automatically
fall back to local simulation, preserving existing behavior.

## Algorithms

- `algorithms.expansion.QuantumLibraryExpansion` – Grover search demonstration.
- `algorithms.teleportation.QuantumTeleportation` – teleports a qubit state using a Bell pair.
- `algorithms.hardware_aware.HardwareAwareAlgorithm` – demonstrates automatic
  hardware selection via `qiskit-ibm-provider` with simulator fallback.
- `algorithms.vqe_demo.run_vqe_demo` – prototype VQE ground state estimation.
- `algorithms.phase_estimation_demo.run_phase_estimation_demo` – prototype phase estimation.

## Backend utilities

- `utils.backend_provider.get_backend` – loads IBM Quantum backends and falls back to `Aer` simulators when hardware is unavailable.

## Pattern Recognition

- `ml_pattern_recognition.PatternRecognizer` – logistic regression based pattern recognizer using placeholder datasets. Use
  `load_placeholder_data` to generate sample data for experiments.
