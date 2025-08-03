# Placeholder Audit Guide

This guide explains how to run the placeholder audit and access results.

## Running the Audit

```bash
python tools/automation_setup.py
```

The script ingests documentation and templates, then invokes the internal
placeholder audit. Findings are written to `databases/analytics.db` in the
`placeholder_audit` table.

## Viewing Results

The dashboard exposes audit findings via the `/placeholder-audit` route:

```bash
python -m web_gui.dashboard_actionable_gui
```

Then visit `http://localhost:5000/placeholder-audit` to fetch the latest
results in JSON form.
