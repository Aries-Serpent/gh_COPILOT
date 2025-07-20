# Root Maintenance Validator

This validator ensures that repository files are organized into the correct enterprise folders.

## Running the Validator

```bash
source .venv/bin/activate
export GH_COPILOT_WORKSPACE=$(pwd)
python scripts/validation/complete_root_maintenance_validator.py
```

The script scans the workspace, computes a compliance score, and writes a Markdown report to `reports/`.

## Understanding the Results

- **Compliance Score** – weighted score based on violation severity. `100%` means no misplacements.
- **Recommendations** – suggested actions, including shell commands for auto-fixes.
- **Auto‑Fix Section** – provides ready-to-run `mv` commands for the most common issues.

Use the recommended commands or run `scripts/orchestrators/unified_wrapup_orchestrator.py` to apply automated fixes.
