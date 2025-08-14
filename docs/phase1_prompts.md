# Phase 1 Prompts

This file contains suggested GitHub issues and workflow snippets generated from the initial repository review.

## Issue Prompts

1. **Refine validation patterns**
   - *Title*: Fix `validate_enterprise_operation` directory matching
   - *Body*: "The current guard in `scripts/continuous_operation_orchestrator.py` removes directories containing the substring `temp`. This wipes important folders like `template_engine` when running ingestion scripts. Update the patterns to avoid accidental deletions (e.g., match `/tmp` or `*_backup`). Include tests for safe execution."

2. **Restore test imports**
   - *Title*: Resolve missing `template_engine` imports for tests
   - *Body*: "`pytest` fails during collection due to `template_engine` modules not found. Ensure the package is included in the repo and adjust import paths so tests in `tests/` run successfully."

3. **Add CI for lint and tests**
   - *Title*: Introduce GitHub Actions workflow for `ruff` and `pytest`
   - *Body*: "Automate style and test checks. Workflow should install dependencies via `setup.sh`, set required environment variables, then run `ruff check .` and `pytest -q --disable-warnings --maxfail=10 --exitfirst`."

4. **Document ingestion process**
   - *Title*: Document safe usage of ingestion scripts
   - *Body*: "Create a guide describing how to initialize `enterprise_assets.db` and ingest docs/templates without triggering validation errors. Include required environment variables and troubleshooting steps."

## Workflow Snippet

```yaml
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest !ONLY ENABLED BY REPO OWNER!
    steps:
      - uses: actions/checkout@v3
      - name: Setup
        run: bash setup.sh
      - name: Run tests
        env:
          GH_COPILOT_WORKSPACE: ${{ github.workspace }}
          GH_COPILOT_BACKUP_ROOT: /tmp/gh_copilot_backup
        run: |
          source .venv/bin/activate
          ruff check .
          pytest -q --disable-warnings --maxfail=10 --exitfirst
```
