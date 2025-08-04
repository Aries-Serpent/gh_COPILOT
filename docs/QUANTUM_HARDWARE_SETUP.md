# Quantum Hardware Setup

Hardware execution is not yet supported. This guide documents the preparatory steps for future IBM Quantum integration. All operations currently run on simulators even when tokens or backend names are provided.

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
The value is recorded for future use, but all executions fall back to the default simulator regardless of this setting.

## 3. CLI Usage
Use the executor CLI or orchestrator to demonstrate where hardware flags will eventually apply (currently no-ops):
```bash
python -m quantum.cli.executor_cli --use-hardware --backend ibm_nairobi
python quantum_integration_orchestrator.py --hardware
```
Both flags validate that `QISKIT_IBM_TOKEN` is present but still run against simulators; backend selection is ignored.

## 4. Expected Outputs
Hardware backends are not invoked. Logs always reflect simulator usage, emitting a warning when hardware options are requested.
