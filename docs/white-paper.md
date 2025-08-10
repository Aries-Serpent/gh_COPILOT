# Project White Paper

## Compliance Formula Implementation

The compliance formula is now **100% implemented** and drives enforcement across the toolkit. The composite score blends lint results, test outcomes, placeholder resolution metrics, and session lifecycle success to provide a single indicator of repository health and feeds the `/api/refresh_compliance` and `/api/compliance_scores` endpoints. For full policy details see the [Governance Standards](GOVERNANCE_STANDARDS.md).

The weighted composite is defined as:

```
score = 0.3 * L + 0.4 * T + 0.2 * P + 0.1 * S
```

Where **L** is the lint score, **T** the test pass rate, **P** the placeholder resolution percentage, and **S** the session success rate. Scores below `0.85` trigger dashboard alerts and notification hooks.

```python
from enterprise_modules.compliance import calculate_compliance_score
score = calculate_compliance_score(
    ruff_issues,
    tests_passed,
    tests_failed,
    placeholders_open,
    placeholders_resolved,
    session_success_rate,
)
```

This helper computes the lint, test, and placeholder ratios and persists the final score to `analytics.db` for dashboard visualization and governance checks.
Dashboard tooltips describe how lint, test, and placeholder scores are derived, and session wrap-ups capture these metrics alongside the composite score for each run.

