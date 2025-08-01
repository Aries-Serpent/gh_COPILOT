# Quantum Utilities

This package provides experimental quantum-inspired utilities used across the
gh_COPILOT toolkit.

> **Note**
> All quantum modules run in simulation unless `qiskit-ibm-provider` is installed and configured with `QISKIT_IBM_TOKEN`.

## Optimizers
- `optimizers.quantum_optimizer.QuantumOptimizer` – classical/quantum hybrid
  optimizer with progress logging. Events are recorded using
  `utils.log_utils._log_event` when executed via higher-level workflows.
  Use `configure_backend()` to automatically load IBM Quantum credentials from
  `QISKIT_IBM_TOKEN` and select either hardware or the local simulator.

## Database Search
- `quantum.quantum_database_search` – lightweight helpers for SQL, NoSQL and
  hybrid search. All queries are logged to `analytics.db` for compliance.

These modules default to simulation mode but can use real IBM Quantum hardware
when `qiskit-ibm-provider` is installed and `QISKIT_IBM_TOKEN` is configured.
Use the `--hardware` flag in `quantum_integration_orchestrator.py` to enable
hardware execution. If hardware is unavailable, the modules automatically fall
back to local simulation.

Hardware usage can also be toggled globally by setting the environment
variable `QUANTUM_USE_HARDWARE` to `"1"`. Modules query this flag when no
explicit option is provided.

## IBM Quantum Access

To run on real IBM Quantum hardware you need an access token from
<https://quantum-computing.ibm.com>. Set the environment variable
`QISKIT_IBM_TOKEN` before executing any demo modules:

```
export QISKIT_IBM_TOKEN="YOUR_API_TOKEN"
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
