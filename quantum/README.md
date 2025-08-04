# Quantum Utilities

This package provides experimental quantum-inspired utilities used across the
gh_COPILOT toolkit.

> **Note**
> Modules automatically attempt hardware execution when IBM Quantum credentials
> are supplied. Set `QISKIT_IBM_TOKEN` or pass a token directly to APIs. If
> hardware access is unavailable the local simulator is used.

## Optimizers
- `optimizers.quantum_optimizer.QuantumOptimizer` – classical/quantum hybrid
  optimizer with progress logging. Events are recorded using
  `utils.log_utils._log_event` when executed via higher-level workflows.
  Use `configure_backend()` for consistent configuration; credentials may be
  supplied via argument or environment variable. Hardware backends are used
  when available, otherwise the local simulator is selected.

## Database Search
- `quantum.quantum_database_search` – lightweight helpers for SQL, NoSQL and
  hybrid search. All queries are logged to `analytics.db` for compliance.

These modules run on IBM Quantum hardware when credentials are provided and the
environment supports the provider. The `--hardware` flag in
`quantum_integration_orchestrator.py` and the `QUANTUM_USE_HARDWARE` environment
variable enable hardware execution with automatic simulator fallback.

## IBM Quantum Access

Set `QISKIT_IBM_TOKEN` or provide a token argument to enable hardware use. When
no token is supplied or the provider fails to initialize, the system falls back
to simulation.

## Algorithms

- `algorithms.expansion.QuantumLibraryExpansion` – Grover search demonstration.
- `algorithms.teleportation.QuantumTeleportation` – teleports a qubit state using a Bell pair.
- `algorithms.hardware_aware.HardwareAwareAlgorithm` – placeholder for automatic
  backend selection; the simulator is always used.
- `algorithms.vqe_demo.run_vqe_demo` – prototype VQE ground state estimation.
- `algorithms.phase_estimation_demo.run_phase_estimation_demo` – prototype phase estimation.

## Backend utilities

  - `utils.backend_provider.get_backend` – selects an IBM Quantum backend when
    credentials are available, otherwise returns the local `Aer` simulator.

## Pattern Recognition

- `ml_pattern_recognition.PatternRecognizer` – logistic regression based pattern
  recognizer using production datasets. Use
  `load_production_data` to fetch samples from `databases/production.db`. The
  ``evaluate`` method supports ``use_quantum=True`` to include a quantum
  similarity score via
  ``quantum_algorithm_library_expansion.quantum_similarity_score``.

### Configuration

1. Ensure `databases/production.db` contains entries in the
   `solution_patterns` table.
2. Load data with `load_production_data()` and train the recognizer using
   `PatternRecognizer.train`.
3. Optionally call `evaluate(..., use_quantum=True)` to compute a quantum
   similarity score alongside accuracy.
