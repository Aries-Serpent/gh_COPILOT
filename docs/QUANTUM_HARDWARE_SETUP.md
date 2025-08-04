# Quantum Hardware Setup

This guide outlines configuration steps for IBM Quantum integration. Modules
attempt hardware execution when valid credentials are provided and gracefully
fall back to local simulators when devices are unavailable.

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
export IBM_BACKEND="ibm_nairobi"
```
If the backend is unavailable the system falls back to `aer_simulator`.

## 3. CLI Usage
Use the executor CLI or orchestrator with hardware flags:
```bash
python -m quantum.cli.executor_cli --use-hardware --backend ibm_nairobi --token "$QISKIT_IBM_TOKEN"
python quantum_integration_orchestrator.py --hardware --backend ibm_nairobi --token "$QISKIT_IBM_TOKEN"
```
If credentials are missing or the provider cannot reach the backend, execution
falls back to simulation and logs a notice.

## 4. Expected Outputs
Logs indicate whether a hardware backend or simulator was used. When hardware
execution succeeds, backend names appear with `[QUANTUM_BACKEND]` tags; otherwise
messages note the simulator fallback.

## 5. Roadmap
Future releases will expand hardware provider support beyond IBM Quantum and add
automated credential management.
