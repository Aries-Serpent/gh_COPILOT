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

Lint, test, placeholder, and session lifecycle outcomes are combined into a single score using
``enterprise_modules.compliance.calculate_compliance_score`` with weights defined in ``SCORE_WEIGHTS`` (30%, 40%, 20%, 10):

```python
from enterprise_modules.compliance import calculate_compliance_score, SCORE_WEIGHTS
score, breakdown = calculate_compliance_score(
    ruff_issues,
    tests_passed,
    tests_failed,
    placeholders_open,
    placeholders_resolved,
    sessions_successful,
    sessions_failed,
)
```

The helper returns the composite ``score`` along with the ratios used to derive it:

- ``lint_score`` – ``max(0, 100 - ruff_issues)``
- ``test_pass_ratio`` – ``tests_passed / (tests_passed + tests_failed)``
- ``placeholder_resolution_ratio`` – ``placeholders_resolved / total_placeholders``
- ``session_success_ratio`` – ``sessions_successful / (sessions_successful + sessions_failed)``

The final ``score`` applies ``SCORE_WEIGHTS`` to ``lint_score``, ``test_pass_ratio * 100``,
``placeholder_resolution_ratio * 100``, and ``session_success_ratio * 100``.

### Session Lifecycle Requirements

The ``session_success_ratio`` is derived from explicit lifecycle events. Every automation run must call
``start_session`` and ``end_session``. Sessions that fail to record a clean end or trigger integrity errors count as failures.
These lifecycle checks align with enterprise policy and feed directly into the composite score.
