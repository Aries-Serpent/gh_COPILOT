# Placeholder Audit Compliance Guide

This guide outlines the procedure for running the placeholder audit and verifying compliance.

## Running the Audit

1. Activate the project virtual environment.
2. Execute `python -m scripts.code_placeholder_audit --workspace-path <path> --analytics-db databases/analytics.db --production-db databases/production.db --dashboard-dir dashboard/compliance`.
3. The script scans for TODO, FIXME, and related markers. Findings are written to `analytics.db` and summarized under `dashboard/compliance`.

## Reviewing Results

- Query `analytics.db` for the `todo_fixme_tracking` table to view individual findings.
- Open the enterprise dashboard and navigate to **Audit Results** to see aggregated counts by placeholder type.

## Compliance

Resolve open placeholders and re-run the audit until the dashboard reports zero findings and a compliant status.
