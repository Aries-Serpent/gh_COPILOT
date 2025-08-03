# Compliance Metrics

This document describes how compliance scores are calculated for the dashboard.

## Compliance Score

The compliance score measures progress resolving placeholders while
accounting for outstanding issues. It is computed as:

```
base = resolved_placeholders / (resolved_placeholders + open_placeholders)
penalty = 0.10 * violation_count + 0.05 * rollback_count
score = max(0, min(1, base - penalty))
```

The score ranges from 0 to 1 and decreases when violations or rollbacks
occur. A missing denominator defaults the base score to 1.0.

## Trend and Latency

The updater records recent compliance scores in `correction_logs`.
The dashboard shows these as the `compliance_trend` to visualize
improvement over time.

Average query latency is derived from entries in the
`performance_metrics` table with `metric_name='query_latency'` and
reported alongside compliance metrics.
