# Quantum Hardware Setup

This guide outlines configuration steps for IBM Quantum integration. Current releases
use simulators by default, but supplying tokens and backend names prepares the system
for real-device execution as soon as access is enabled.

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

## 2. Backend Selection
Specify a backend name via `IBM_BACKEND`:
```bash
export IBM_BACKEND="ibmq_qasm_simulator"
```
The orchestrator attempts to use this backend; if unavailable it falls back to the default simulator.

## 3. CLI Usage
Use the executor CLI or orchestrator with hardware flags:
```bash
python -m quantum.cli.executor_cli --use-hardware --backend ibm_nairobi
python quantum_integration_orchestrator.py --hardware
```
If the specified backend is unavailable, execution falls back to simulators with a warning.

## 4. Expected Outputs
When hardware access is configured, logs reflect the chosen backend. Without access,
the system logs a fallback message and uses the simulator.

## 5. Roadmap
Upcoming releases will introduce a `QuantumExecutor` module that manages credential
authentication, backend selection, and automatic simulator fallback.
