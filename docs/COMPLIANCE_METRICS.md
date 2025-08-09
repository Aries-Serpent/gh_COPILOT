# Compliance Metrics

This document describes how compliance scores are calculated for the dashboard.

## Compliance Score

The compliance score measures progress resolving placeholders while
accounting for outstanding issues. Anti-recursion validation via
`enterprise_modules.compliance.enforce_anti_recursion` must succeed before
any score is recorded. The score is computed as:

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
``enterprise_modules.compliance.calculate_compliance_score`` with
weights of 30%, 50% and 20% respectively:

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
- ``test_score = (tests_passed / total_tests) * 100`` where
  ``total_tests`` is the sum of passed and failed tests
- ``placeholder_score = (placeholders_resolved / total_placeholders) * 100``
  where ``total_placeholders`` is the sum of open and resolved placeholders

The final compliance score is the weighted sum of these components and is
persisted to ``analytics.db`` for dashboard visualization:

``0.3 * lint_score + 0.5 * test_score + 0.2 * placeholder_score``

## Code Quality Score Helper

The dashboard exposes a richer breakdown via
``enterprise_modules.compliance.calculate_code_quality_score``:

```python
from enterprise_modules.compliance import calculate_code_quality_score
score, breakdown = calculate_code_quality_score(
    ruff_issues,
    tests_passed,
    tests_failed,
    placeholders_open,
    placeholders_resolved,
)
```

This helper returns the composite score along with the ratios used to derive
it:

- ``lint_score`` – ``max(0, 100 - ruff_issues)``
- ``test_pass_ratio`` – ``tests_passed / (tests_passed + tests_failed)``
- ``placeholder_resolution_ratio`` – ``placeholders_resolved / total_placeholders``

The final ``score`` is the mean of ``lint_score``, ``test_pass_ratio * 100`` and
``placeholder_resolution_ratio * 100``.
