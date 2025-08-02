# Quantum Hardware Setup

This guide explains how to run gh_COPILOT components on IBM Quantum hardware.

## 1. Acquire a Token
1. Create an IBM Quantum account.
2. Generate an API token from the account dashboard.
3. Set the token as an environment variable:
   ```bash
   export QISKIT_IBM_TOKEN="your_token_here"
   ```
   Alternatively, place the token in `config/qiskit.json` as:
   ```json
   {"QISKIT_IBM_TOKEN": "your_token_here"}
   ```

## 2. Optional Backend Selection
Specify a backend name via `IBM_BACKEND`:
```bash
export IBM_BACKEND="ibmq_qasm_simulator"
```
If unset, the default simulator is used.

## 3. CLI Usage
Use the executor CLI to force hardware execution:
```bash
python -m quantum.cli.executor_cli --use-hardware --backend ibm_nairobi
```
The flag validates that `QISKIT_IBM_TOKEN` is present and selects the requested backend.

## 4. Expected Outputs
When hardware is available, logs include `[QUANTUM_BACKEND]` and the selected backend name. If initialization fails, a warning is emitted and the Aer simulator is used instead.
