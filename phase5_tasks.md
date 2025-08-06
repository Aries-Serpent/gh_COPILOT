# Phase 5 Compliance Scoring

The compliance score blends linting, testing, and placeholder hygiene:

- **Lint component (L):** `L = max(0, 100 - issues)` where `issues` is the number of Ruff findings.
- **Test component (T):** `T = passed / (passed + failed) * 100` from pytest results.
- **Placeholder component (P):** `P = (resolved / (open + resolved)) * 100` with a default of `100` when no placeholders exist.

The weighted composite score is:

```
score = 0.3 * L + 0.5 * T + 0.2 * P
```

This applies weights of **30%** to lint results, **50%** to tests, and **20%** to placeholder cleanup. The score is stored in `analytics.db` and surfaced at `/dashboard/compliance`.

Implemented in [`calculate_composite_score`](enterprise_modules/compliance.py), the function returns the overall score and a breakdown of each weighted component for dashboard use.
