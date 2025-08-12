# Quantum Integration Plan

The orchestrator supports multiple quantum providers behind a single command
line entry point.  Usage:

```
python quantum_integration_orchestrator.py --provider <simulator|ibm|ionq|dwave>
```

## Configuration

Each provider relies on an environment token.  When the token is missing the
system falls back to the simulator backend.

| Provider | Token | Notes |
| -------- | ----- | ----- |
| `ibm`    | `QISKIT_IBM_TOKEN` | Optional `IBM_BACKEND` selects a specific device. |
| `ionq`   | `IONQ_API_KEY` | Supports `IONQ_BACKEND` for backend selection. |
| `dwave`  | `DWAVE_API_TOKEN` | `DWAVE_SOLVER` selects the solver. |

## Roadmap

1. **Stub Backends:** Initial release ships with stub implementations so the
   integration flow can be exercised without vendor SDKs.
2. **Provider SDK Hooks:** Future updates will replace the stubs with actual
   adapters that call provider APIs when the respective SDKs are installed.
3. **Hybrid Workflows:** The orchestrator will expose hooks to combine classical
   and quantum workloads, driven by the new provider abstraction.

This document will evolve as hardware integrations progress.

