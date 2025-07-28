# Documentation Metrics Validation Failure

The continuous integration job `docs-validation.yml` failed because it attempted
to execute `scripts/docs_metrics_validator.py`, which did not exist in the
repository. The correct validation script was named
`scripts/validate_docs_metrics.py`. The workflow therefore raised a
`FileNotFoundError` and halted documentation metrics validation.

## Remediation

An alias script named `scripts/docs_metrics_validator.py` has been added. It
wraps `validate_docs_metrics.validate()` and preserves the existing command line
interface. The CI workflow now invokes this wrapper or falls back to the module
path to ensure compatibility across environments.
Documentation references running the validator as a module:
`python -m scripts.docs_metrics_validator`.

## Preventive Steps

* Maintain consistency between workflow configuration and script names.
* Validate CI changes locally with `pytest` and `ruff` before merging.
* Include wrapper scripts when renaming utilities to avoid breaking existing
  automation.
