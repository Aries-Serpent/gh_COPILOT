# Auditing Workflow

This project includes an automated placeholder audit to keep the codebase compliant.

1. Run `scripts/code_placeholder_audit.py --task-report reports/placeholder_tasks.json`
   to scan the workspace. It logs unresolved placeholders to `analytics.db`, writes a
   task report (JSON or Markdown), and updates
   `dashboard/compliance/placeholder_summary.json`.
2. Use `scripts/placeholder_enforcer.py --report reports/placeholder_tasks.json` to
   open tracking tickets or PR stubs for each unresolved placeholder. The enforcer
   marks matching entries in `analytics.db.todo_fixme_tracking` and refreshes the
   dashboard metrics.
3. When placeholders are removed from the codebase, rerun the audit with
   `--update-resolutions` to automatically purge resolved entries from the tracking table.
4. Pass `--apply-fixes` to remove placeholder comments directly from source files. The
   audit also cleans up any placeholder metadata that is no longer needed.
5. `dashboard/compliance_metrics_updater.py` reads `analytics.db` and recomputes the
   `compliance_score` (0–100%) based on remaining open or ticketed placeholders. Run it
   to refresh the dashboard after each audit/enforcement.

The `DatabaseComplianceChecker` now corrects common issues automatically. Its
`correct_file` routine removes placeholder markers (such as `TODO` or
`PLACEHOLDER` comments), trims trailing whitespace, ensures files end with a
newline, and records the outcome to `analytics.db`. If a file cannot be
corrected, the failure and error message are logged for further review.

These scripts follow the repository's dual‑copilot and database‑first protocols. Ensure
that the virtual environment is active and tests pass before committing changes.
