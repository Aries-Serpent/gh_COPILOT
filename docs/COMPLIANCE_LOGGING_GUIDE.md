# Compliance Logging Guide

This guide outlines how correction events are captured and surfaced in the
dashboard.

## Correction Logging

- `scripts/correction_logger_and_rollback.py` records every correction in
  `databases/analytics.db` and writes a summary to
  `dashboard/compliance/correction_summary.json`.
- Each entry includes the affected file path, rationale, correction type,
  compliance score, compliance delta, session identifier, and rollback
  reference.

## Metrics Ingestion

- `dashboard/compliance_metrics_updater.py` loads the correction summary and
  merges the data with other compliance metrics.
- Each compliance run records a **composite score** and its component
  contributions (lint, tests, and placeholder resolution) into
  `databases/analytics.db` under the `compliance_scores` table.
- The updater exposes a list of correction logs, the latest composite score and
  a trend of recent scores alongside placeholder and violation statistics.

## Dashboard Display

- `dashboard/templates/metrics.html` presents the aggregated compliance score
  and renders each correction log with its individual score and rationale.
- `dashboard/enterprise_dashboard.py` provides a `/compliance-metrics` route
  returning the most recent composite score, its component breakdown, and a
  history of prior scores for trend visualizations.

Running `compliance_metrics_updater.py` after executing the correction logger
keeps the dashboard synchronized with the latest corrections and compliance
scores.

