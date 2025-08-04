# Quantum Integration Plan

## Module Architecture
- **QuantumAlgorithmRegistry**: central registry for available algorithms.
- **QuantumExecutor**: manages backend selection and executes registered algorithms.
- **QuantumIntegrationOrchestrator**: high level interface that coordinates algorithm execution using the registry and executor.

## Simulation Fallback
- Hardware execution is not implemented; even with `QISKIT_IBM_TOKEN` the system uses `qasm_simulator` from `qiskit`.
- Interfaces mirror potential hardware usage for future parity.
- Maintains identical interfaces so future hardware support can plug in without API changes.

## Placeholder Modules

Prototype implementations reside under `scripts/quantum_placeholders/`.
Each module defines `PLACEHOLDER_ONLY = True`, and build tooling
detects this marker to exclude them during packaging. Importing a
placeholder when `GH_COPILOT_ENV` is set to `"production"` raises a
`RuntimeError`, keeping production deployments free of unfinished
quantum code while preserving importability for planning.
