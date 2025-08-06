# Quantum Integration Plan

## Module Architecture
- **QuantumAlgorithmRegistry**: central registry for available algorithms.
- **QuantumExecutor**: manages backend selection and executes registered algorithms.
- **QuantumIntegrationOrchestrator**: high level interface that coordinates algorithm execution using the registry and executor.

## Simulation Only
- Hardware execution is not implemented; the integration always uses
  `qasm_simulator` from `qiskit`.
- Interfaces mirror potential hardware usage for future parity but currently
  ignore hardware-specific settings.
- Maintains identical interfaces so future hardware support can plug in without
  API changes.

## Hardware Requirements
- Future hardware execution will require `qiskit` plus `qiskit-ibm-provider`
  and a valid IBM Quantum token provided via the `QISKIT_IBM_TOKEN` environment
  variable.
- Environment variables such as `QUANTUM_USE_HARDWARE` and `IBM_BACKEND` are
  currently **no-ops**; the system always runs on simulators.

## Placeholder Modules

Prototype implementations reside under `scripts/quantum_placeholders/`.
Each module defines `PLACEHOLDER_ONLY = True`, and build tooling
detects this marker to exclude them during packaging. Importing a
placeholder when `GH_COPILOT_ENV` is set to `"production"` raises a
`RuntimeError`, keeping production deployments free of unfinished
quantum code while preserving importability for planning.
