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

## Code Quality Composite Score

Lint, test and placeholder results are combined into a single score using
``enterprise_modules.compliance.calculate_compliance_score``:

```
from enterprise_modules.compliance import calculate_compliance_score
score = calculate_compliance_score(
    ruff_issues,
    tests_passed,
    tests_failed,
    placeholders_open,
    placeholders_resolved,
)
```

The helper computes three component scores:

- ``lint_score = max(0, 100 - ruff_issues)``
- ``test_score = (tests_passed / total_tests) * 100``
- ``placeholder_score = (placeholders_resolved / total_placeholders) * 100``

The final compliance score is the arithmetic mean of these components and is
persisted to ``analytics.db`` for dashboard visualization.
