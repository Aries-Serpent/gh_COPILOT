# Phase 5 Compliance Scoring

The compliance score blends linting, testing, and placeholder hygiene:

- **Lint component (L):** `L = max(0, 100 - issues)` where `issues` is the number of Ruff findings.
- **Test component (T):** `T = passed / (passed + failed) * 100` from pytest results.
- **Placeholder component (P):** `P = max(0, 100 - 10 * placeholders)` where `placeholders` counts TODO/FIXME markers.

The weighted composite score is:

```
score = 0.3 * L + 0.5 * T + 0.2 * P
```

This score is stored in `analytics.db` and surfaced at `/dashboard/compliance`.
