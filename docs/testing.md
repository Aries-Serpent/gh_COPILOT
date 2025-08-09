# Testing Guide

## Integration Test Suite

The repository includes an integration test suite that exercises cross-module workflows. Run the suite directly with:

```bash
pytest tests/integration
```

## Safe Pytest Runner

Use the safe runner to execute tests with optional coverage and JSON reporting. It automatically enables plugins when available and writes a summary file.

```bash
python scripts/run_tests_safe.py                 # run entire suite
python scripts/run_tests_safe.py --target tests/integration --output artifacts/integration_summary.json
```

The runner ensures consistent options and prevents long-running hangs by enforcing timeouts.
