# Quantum Hardware Setup

This guide outlines placeholder configuration steps for eventual IBM Quantum
integration. Current releases operate **only** in simulator mode; tokens and
backend names are stored for future use but have no effect until real-device
access is enabled. Following these steps will not enable hardware execution
today.

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
Specify a backend name via `IBM_BACKEND` (currently ignored):
```bash
export IBM_BACKEND="ibmq_qasm_simulator"
```
The orchestrator records this value but always uses the default simulator.

## 3. CLI Usage
Use the executor CLI or orchestrator with hardware flags (placeholders only):
```bash
python -m quantum.cli.executor_cli --use-hardware --backend ibm_nairobi
python quantum_integration_orchestrator.py --hardware
```
Regardless of backend settings, execution always uses simulators and logs a notice.

## 4. Expected Outputs
When hardware access becomes available, logs will reflect the chosen backend. Until then,
the system logs that simulation mode is enforced.

## 5. Roadmap
Upcoming releases will introduce a `QuantumExecutor` module that manages credential
authentication, backend selection, and automatic simulator fallback.
