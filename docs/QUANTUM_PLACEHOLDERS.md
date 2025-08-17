# Quantum Placeholders Roadmap

**Last Updated:** 2025-08-17T04:05:14Z

## Scope
Replace pass-through stubs in `scripts/quantum_placeholders/` with minimal parity-verifying algorithms and define backend API hooks (Qiskit, IonQ, D-Wave) without activation.

## Milestones
1. Parity Algorithm (mock simulators) — DONE
2. API Hook Scaffolds with Token Checks — DONE
3. Prototype Tests — DONE
4. Hardware Integration (future) — PENDING
5. Real Simulator Cross-Checks with Tolerance — PENDING

## Parity Criteria
Given two simulators s1, s2 and circuit c, ensure distance(s1(c), s2(c)) ≤ ε (default via Hellinger metric with relaxed threshold 0.35 for mocks).

## Backend Hooks
- `hardware_hooks/qiskit.py` → env `QISKIT_API_TOKEN`
- `hardware_hooks/ionq.py` → env `IONQ_API_TOKEN`
- `hardware_hooks/dwave.py` → env `DWAVE_API_TOKEN`

## Test Matrix (prototype)
- Identity, RX(θ), Simple Bell

> Note: **DO NOT ACTIVATE ANY GitHub Actions**.
