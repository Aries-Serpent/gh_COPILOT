# Quantum Utilities

This package provides experimental quantum-inspired utilities used across the
gh_COPILOT toolkit.

> **Note**
> Utilities default to local Qiskit simulators. When
> `use_hardware=True` and a valid IBM Quantum token is supplied via
> the `QISKIT_IBM_TOKEN` environment variable (or constructor argument),
> `QuantumExecutor` will attempt to initialize the backend named by
> `IBM_BACKEND`.

## Framework and Models

- `framework` – core abstractions for backend management. The
  `QuantumExecutor` automatically falls back to a lightweight simulator when
  no quantum hardware is available.
- `models` – base interfaces for quantum-enabled models that build circuits and
  execute them through the framework.

### Extending Models

Subclass :class:`quantum.models.QuantumModel` and implement ``build_circuit``
to describe the quantum workload. For robust behavior, override ``run`` and
provide a classical fallback when quantum execution fails. The
``ParityModel`` demonstrates this pattern by computing the parity of a list of
bits on the simulator and reverting to a classical parity check if an error
occurs.

## Optimizers
- `optimizers.quantum_optimizer.QuantumOptimizer` – classical/quantum hybrid
  optimizer with progress logging. Events are recorded using
  `utils.log_utils._log_event` when executed via higher-level workflows.
Use `configure_backend()` for consistent configuration; credentials may be
supplied via argument or environment variable. The function always selects the
local simulator and ignores hardware-specific settings.

## Database Search
- `quantum.quantum_database_search` – lightweight helpers for SQL, NoSQL and
  hybrid search. All queries are logged to `analytics.db` for compliance.

These modules default to simulators when no IBM credentials are available.
The `--hardware` flag in `quantum_integration_orchestrator.py` and the
`QUANTUM_USE_HARDWARE` environment variable enable hardware execution when
`QISKIT_IBM_TOKEN` and a usable backend are supplied.

## IBM Quantum Access

Provide an IBM Quantum token via `QISKIT_IBM_TOKEN` (or the ``token`` argument)
to allow `QuantumExecutor` to run circuits on real hardware. If the provider or
backend cannot be loaded, the executor automatically falls back to the local
simulator.

## Algorithms

- `algorithms.expansion.QuantumLibraryExpansion` – Grover search demonstration.
- `algorithms.teleportation.QuantumTeleportation` – teleports a qubit state using a Bell pair.
- `algorithms.hardware_aware.HardwareAwareAlgorithm` – placeholder for automatic
  backend selection; the simulator is always used.
- `algorithms.vqe_demo.run_vqe_demo` – prototype VQE ground state estimation.
- `algorithms.phase_estimation_demo.run_phase_estimation_demo` – prototype phase estimation.

## Backend utilities

  - `utils.backend_provider.get_backend` – returns the local `Aer` simulator.
    Backend selection logic for real hardware is reserved for future phases.

## Pattern Recognition

- `ml_pattern_recognition.PatternRecognizer` – logistic regression based pattern
  recognizer using production datasets. Use
  `load_production_data` to fetch samples from `databases/production.db`. The
 ``evaluate`` method supports ``use_quantum=True`` to include a quantum
 similarity score via
 ``quantum_algorithm_library_expansion.quantum_similarity_score``.

## Test Coverage and Benchmark

Recent tests provide full coverage for `gate_ops` and `sim_runner`:

```
quantum/gate_ops.py      36 statements   100% coverage
quantum/sim_runner.py    16 statements   100% coverage
```

A cProfile run of a two-qubit Bell circuit completes in roughly 0.001 s with
the majority of time spent in NumPy's `kron` function, confirming efficient
matrix operations.

### Configuration

1. Ensure `databases/production.db` contains entries in the
   `solution_patterns` table.
2. Load data with `load_production_data()` and train the recognizer using
   `PatternRecognizer.train`.
3. Optionally call `evaluate(..., use_quantum=True)` to compute a quantum
   similarity score alongside accuracy.
