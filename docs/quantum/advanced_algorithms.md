# Advanced Quantum Algorithms

This guide documents the Qiskit-based reference implementations
available in `quantum/advanced_quantum_algorithms.py`.

> **Note**
> All examples run on simulator backends only. Installing `qiskit-ibm-provider` or supplying IBM Quantum tokens has no effect because hardware execution is not supported.

## Grover Search

```python
from quantum.advanced_quantum_algorithms import grover_search_qiskit

result = grover_search_qiskit("11")
print(result)  # '11'
```

## Quantum Phase Estimation

```python
from quantum.advanced_quantum_algorithms import phase_estimation_qiskit

phase = phase_estimation_qiskit(0.125, precision=3)
print(phase)
```

Both functions use Qiskit's simulator backend and require the
`qiskit` package to be installed; real hardware backends are ignored.
