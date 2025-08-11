# Phase 5 Compliance Scoring

The compliance score blends linting, testing, placeholder hygiene, and session health:

- **Lint component (L):** `L = max(0, 100 - issues)` where `issues` is the number of Ruff findings.
- **Test component (T):** `T = passed / (passed + failed) * 100` from pytest results.
- **Placeholder component (P):** `P = (resolved / (open + resolved)) * 100` with a default of `100` when no placeholders exist.
- **Session component (S):** `S = successful / (successful + failed) * 100` defaulting to `100` when no sessions recorded.

The weighted composite score uses ``SCORE_WEIGHTS`` (30%, 40%, 20%, 10):

```
score = 0.3 * L + 0.4 * T + 0.2 * P + 0.1 * S
```

Implemented in [`calculate_compliance_score`](enterprise_modules/compliance.py), the function returns the overall score and a breakdown of each weighted component for dashboard use.
