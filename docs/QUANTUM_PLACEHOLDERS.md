# Quantum Placeholders Roadmap

**Last Updated:** 2025-08-17T05:00:00Z

## Scope
Replace pass-through stubs in `scripts/quantum_placeholders/` with minimal parity-verifying algorithms and define backend API hooks (Qiskit, IonQ, D-Wave) without activation.

## Milestones
1. Parity Algorithm (mock simulators) — DONE
2. API Hook Scaffolds with Token Checks — DONE
3. Backend Interfaces with Simulator Fallbacks — DONE
4. Prototype Tests — DONE
5. Hardware Integration (future) — PENDING
6. Real Simulator Cross-Checks with Tolerance — PENDING

## Parity Criteria
Given two simulators s1, s2 and circuit c, ensure distance(s1(c), s2(c)) ≤ ε (default via Hellinger metric with relaxed threshold 0.35 for mocks).

## Backend Hooks
- `hardware_hooks/qiskit.py` → env `QISKIT_IBM_TOKEN`
- `hardware_hooks/ionq.py` → env `IONQ_API_KEY`
- `hardware_hooks/dwave.py` → env `DWAVE_API_TOKEN`
Each hook attempts to use real hardware when the provider SDK and tokens are present,
executing a trivial circuit and falling back to a local simulator when unavailable.

## Test Matrix (prototype)
- Identity, RX(θ), Simple Bell

> Note: **DO NOT ACTIVATE ANY GitHub Actions**.
