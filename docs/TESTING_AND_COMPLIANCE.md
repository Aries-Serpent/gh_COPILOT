# Testing and Compliance

This project uses `pytest` for automated testing and `pytest-cov` for coverage
reporting. To run the test suite with coverage enabled:

```
pytest
```

Individual tests can be executed with:

```
pytest path/to/test_file.py
```

Linting is provided by `ruff`:

```
ruff check <paths>
```

Placeholder audits can be simulated via:

```
python scripts/code_placeholder_audit.py --simulate
```

All outputs should be reviewed to ensure that no placeholders remain and that
coverage metrics are captured.
