# Phase 5 Composite Compliance Score

The composite compliance score blends linting, tests, and placeholder hygiene into a single 0–100 metric.

## Components

- **Lint (L):** `L = max(0, 100 - issues)` where *issues* is the number of ruff findings.
- **Tests (T):** `T = passed / (passed + failed) * 100`; defaults to `0` if no tests run.
- **Placeholders (P):** `P = resolved / (open + resolved) * 100`; defaults to `100` when no placeholders exist.

## Formula

```
score = 0.3 * L + 0.5 * T + 0.2 * P
```

The function `calculate_composite_score` in `enterprise_modules/compliance.py` returns the overall score and a breakdown of each weighted component, allowing dashboards to surface detailed compliance metrics.
