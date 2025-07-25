# Quantum Utilities

This package provides experimental quantum-inspired utilities used across the
gh_COPILOT toolkit.

## Optimizers
- `optimizers.quantum_optimizer.QuantumOptimizer` – classical/quantum hybrid
  optimizer with progress logging. Events are recorded using
  `utils.log_utils._log_event` when executed via higher-level workflows.

## Database Search
- `quantum.quantum_database_search` – lightweight helpers for SQL, NoSQL and
  hybrid search. All queries are logged to `analytics.db` for compliance.

These modules are simulation-focused and designed to run without actual quantum
hardware. They can be imported via the `quantum` package.
