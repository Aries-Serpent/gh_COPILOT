# Placeholder Audit Guide

This guide explains how to run the placeholder audit and access results.

## Running the Audit

```bash
python tools/automation_setup.py
```

The script ingests documentation and templates, then invokes the internal
placeholder audit. Findings are written to `databases/analytics.db` in the
`placeholder_audit` table.

The audit prints a list of actionable tasks for every unresolved
placeholder so developers can quickly remove them. When the codebase is
clean, the output confirms that no work remains:

```
[SUCCESS] No TODO or FIXME placeholders found
```

### Applying Suggestions Automatically

Use the `--apply-suggestions` flag to apply simple fixes generated for
each TODO or FIXME. Lines are updated in place and resolved entries are
removed from the audit:

```bash
python scripts/code_placeholder_audit.py --apply-suggestions \
  --workspace-path "$GH_COPILOT_WORKSPACE" \
  --analytics-db databases/analytics.db \
  --production-db databases/production.db \
  --dashboard-dir dashboard/compliance
```

Unresolved placeholders are recorded in `analytics.db` under the
`unresolved_placeholders` table with their file paths and line numbers.

## Viewing Results

The dashboard exposes audit findings via the `/placeholder-audit` route:

```bash
python dashboard/enterprise_dashboard.py
```

Then visit `http://localhost:5000/placeholder-audit` to fetch the latest
results in JSON form.

## CI Integration

Fail builds if placeholders remain by running the audit with
`--fail-on-findings`:

```
python scripts/code_placeholder_audit.py --fail-on-findings --simulate \
  --workspace-path "$GH_COPILOT_WORKSPACE" \
  --analytics-db databases/analytics.db \
  --production-db databases/production.db \
  --dashboard-dir dashboard/compliance
```

The command exits with a non-zero status when unresolved placeholders are
found, enabling CI pipelines to block merges until cleanup is complete.
