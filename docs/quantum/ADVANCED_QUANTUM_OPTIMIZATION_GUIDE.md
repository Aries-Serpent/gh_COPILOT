# ADVANCED QUANTUM OPTIMIZATION GUIDE

This guide outlines how to extend the existing quantum module with an advanced optimization algorithm. It assumes familiarity with the repository's quantum package and the base `QuantumAlgorithmBase` class.

## 1. Create the Module
1. Navigate to `quantum/algorithms/`.
2. Create a new file named `advanced_optimization.py` that defines `AdvancedQuantumOptimizer` inheriting from `QuantumAlgorithmBase`.
3. Implement `get_algorithm_name()` to return a descriptive name.
4. Implement `execute_algorithm()` to perform the optimization logic. Use the existing algorithms as references for structure and logging practices.

## 2. Implement the Algorithm Logic
1. Prepare your quantum circuit using Qiskit or another supported framework.
2. Configure a suitable backend (simulator or hardware if available).
3. Encode the problem instance into the circuit using variational forms or oracle-based methods.
4. Apply iterative optimization (e.g., variational quantum eigensolver or quantum annealing) while logging progress via the base class utilities.
5. Record execution statistics with fidelity and performance metrics for later analysis.

## 3. Add a Command-Line Interface
1. Provide an entry point function `main()` that parses arguments such as workspace path, number of iterations, and backend selection.
2. Ensure the CLI prints status messages using the text-based indicators defined in the base class (`TEXT_INDICATORS`).
3. Update `setup.cfg` or the relevant packaging file if a console script entry point is desired.

## 4. Update Documentation
1. Add a short description of the new algorithm to `docs/quantum/INDEX.md` with a link to this guide.
2. Document expected inputs, outputs, and example commands in `README.md` if user-facing.
3. Include any configuration options or environment variables required to run the optimizer.

## 5. Testing and Validation
1. Create tests in `tests/` that instantiate `AdvancedQuantumOptimizer` and verify it runs without errors using a simulated backend.
2. Validate that execution statistics are stored and that progress logging occurs as expected.
3. Run `ruff` and `pytest` to ensure linting and tests pass before committing.

---
*Document version 1.0 – Enterprise guidance for extending quantum capabilities*
