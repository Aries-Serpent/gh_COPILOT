## Compliance Testing Procedures

This project uses `pytest` and `ruff` to validate changes and enforce code quality.

### Running Tests

```bash
pytest tests/test_validation_package.py tests/compliance_test_suite.py \
 2>&1 | tee logs/compliance_monitoring/pytest.log
```

The test run writes its output to `logs/compliance_monitoring/pytest.log` so any
failures can be reviewed after execution.

### Placeholder Audit

The compliance test suite invokes the placeholder audit module in simulation
mode. To run it directly:

```bash
python -m scripts.code_placeholder_audit --simulate \
  --workspace-path "$(pwd)" --analytics-db databases/analytics.db \
  --production-db databases/production.db --dashboard-dir dashboard/compliance
```

### Linting

Run `ruff` on modified files before committing:

```bash
ruff tests/test_validation_package.py tests/compliance_test_suite.py
```

These steps help ensure the repository remains in a compliant state.

