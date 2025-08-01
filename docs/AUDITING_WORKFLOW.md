# Auditing Workflow

This project includes an automated placeholder audit to keep the codebase compliant.

1. Run `scripts/code_placeholder_audit.py` to scan the workspace. It logs unresolved
   placeholders to `analytics.db` and updates `dashboard/compliance/placeholder_summary.json`.
2. When placeholders are removed from the codebase, rerun the audit with
   `--update-resolutions` to automatically purge resolved entries from the tracking table.
3. Pass `--apply-fixes` to remove placeholder comments directly from source files. The
   audit also cleans up any placeholder metadata that is no longer needed.
4. `dashboard/compliance_metrics_updater.py` reads `analytics.db` and recomputes the
   `compliance_score` based on remaining open placeholders. Run it to refresh the
   dashboard after each audit.

These scripts follow the repository's dual‑copilot and database‑first protocols. Ensure
that the virtual environment is active and tests pass before committing changes.
