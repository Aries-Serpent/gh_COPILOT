# Compliance Logging Guide

This guide outlines how correction events are captured and surfaced in the
dashboard.

## Correction Logging

- `scripts/correction_logger_and_rollback.py` records every correction in
  `databases/analytics.db` and writes a summary to
  `dashboard/compliance/correction_summary.json`.
- Each entry includes the affected file path, rationale, compliance score and
  rollback reference.

## Metrics Ingestion

- `dashboard/compliance_metrics_updater.py` loads the correction summary and
  merges the data with other compliance metrics.
- The updater exposes a list of correction logs and an average compliance score
  alongside placeholder and violation statistics.

## Dashboard Display

- `dashboard/templates/metrics.html` presents the aggregated compliance score
  and renders each correction log with its individual score and rationale.

Running `compliance_metrics_updater.py` after executing the correction logger
keeps the dashboard synchronized with the latest corrections and compliance
scores.

