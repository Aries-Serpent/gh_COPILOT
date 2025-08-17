# Quantum Simulation Setup

> **Status:** Hardware execution is not supported. This guide is retained for
future reference. Current modules always use local simulators and ignore all
hardware flags; tokens and backend selections are treated as placeholders.

This document outlines prospective configuration steps for IBM Quantum
integration. At present, modules run exclusively in simulation mode.

## 1. Acquire a Token (Future)
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
   Tokens are currently unused and act solely as placeholders until
   hardware integration lands.

## 2. Backend Selection (Future)
Specify a backend name via `IBM_BACKEND`:
```bash
export IBM_BACKEND="ibm_nairobi"
```
Backend variables are ignored today; the system always uses `aer_simulator`.

## 3. CLI Usage
Hardware flags are accepted but have no effect. Example commands run
in simulation regardless of the parameters:
```bash
python -m quantum.cli.executor_cli --use-hardware --backend ibm_nairobi --token "$QISKIT_IBM_TOKEN"
python quantum_integration_orchestrator.py --hardware --backend ibm_nairobi --token "$QISKIT_IBM_TOKEN"
```
All executions log that the simulator was used.

## 4. Expected Outputs
Logs currently always show `[QUANTUM_BACKEND] aer_simulator`; hardware backends
are not reachable.

## 5. Roadmap
Future releases will expand hardware provider support beyond IBM Quantum and add
automated credential management. Track progress in
[STUB_MODULE_STATUS.md](STUB_MODULE_STATUS.md) and
[QUANTUM_PLACEHOLDERS.md](QUANTUM_PLACEHOLDERS.md).


### Installation
```bash
pip install -r requirements.txt
```

> Note: This project requires `PyYAML>=6.0.1`.
