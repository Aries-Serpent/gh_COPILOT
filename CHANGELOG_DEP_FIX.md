# Dependency Hardening Change Log

## Summary of Changes

* Ensured global tqdm in base deps: added tqdm to base dependencies
* Ensured typer available in dev/test: added typer to dev extras
* CI (non-activating) recommendations:
- Suggest adding `pip install .[dev]` before test steps in ci.yml (NOT auto-applied).
- Suggest adding `pip install .[dev]` before test steps in artifact_lfs.yml (NOT auto-applied).
- Suggest adding `pip install .[dev]` before test steps in daily-whitepaper.yml (NOT auto-applied).
- Suggest adding `pip install .[dev]` before test steps in lfs-zip-guard.yml (NOT auto-applied).
- Suggest adding `pip install .[dev]` before test steps in governance.yml (NOT auto-applied).
- Suggest adding `pip install .[dev]` before test steps in docs-validation.yml (NOT auto-applied).
- Suggest adding `pip install .[dev]` before test steps in status_drift.yml (NOT auto-applied).
- Suggest adding `pip install .[dev]` before test steps in status-reconciler.yml (NOT auto-applied).
- Suggest adding `pip install .[dev]` before test steps in docs-status.yml (NOT auto-applied).
- Suggest adding `pip install .[dev]` before test steps in lfs-guard.yml (NOT auto-applied).
- Suggest adding `pip install .[dev]` before test steps in dashboard-compliance.yml (NOT auto-applied).
* Validator run exit=1
* Created smoke test: tests/test_dependencies_imports.py
* Pruning advisories:
- Detected multiple dependency declaration surfaces; prefer pyproject.toml as source-of-truth. Consider pruning duplicates.
* pytest run exit=4

### Notes
- DO NOT ACTIVATE ANY GitHub Actions files; suggestions are non-executable guidance only.

### Remaining Errors
- See .codex_error_log.md for research-ready questions.
