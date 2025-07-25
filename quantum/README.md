# Quantum Module

This package provides experimental quantum-inspired utilities including
optimizers and database search helpers. The primary entry points are:

- `optimizers/quantum_optimizer.py` – simulated annealing and hybrid routines.
- `quantum_database_search.py` – SQL/NoSQL search with analytics logging.

These components log events to `analytics.db` via `utils.log_utils._log_event`.
Use them for deterministic tests only; results are not true quantum outputs.
