# Phase 5 Composite Compliance Score

The composite compliance score blends linting, tests, placeholder hygiene, and session health into a single 0–100 metric.

## Components

- **Lint (L):** `L = max(0, 100 - issues)` where *issues* is the number of ruff findings.
- **Tests (T):** `T = passed / (passed + failed) * 100`; defaults to `0` if no tests run.
- **Placeholders (P):** `P = resolved / (open + resolved) * 100`; defaults to `100` when no placeholders exist.
- **Sessions (S):** `S = successful / (successful + failed) * 100`; defaults to `100` when no sessions recorded.

## Formula

```
score = 0.3 * L + 0.4 * T + 0.2 * P + 0.1 * S
```

The function `calculate_compliance_score` in `enterprise_modules/compliance.py` returns the overall score and a breakdown of each weighted component, allowing dashboards to surface detailed compliance metrics.
