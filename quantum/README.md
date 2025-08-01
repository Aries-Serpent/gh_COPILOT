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

## Algorithms

- `algorithms.expansion.QuantumLibraryExpansion` – Grover search demonstration.
- `algorithms.teleportation.QuantumTeleportation` – teleports a qubit state using a Bell pair.

## Backend utilities

- `utils.backend_provider.get_backend` – loads IBM Quantum backends and falls back to `Aer` simulators when hardware is unavailable.
