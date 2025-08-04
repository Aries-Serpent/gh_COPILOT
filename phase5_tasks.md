# Phase 5 Compliance Scoring

The compliance score blends linting, testing, and placeholder hygiene:

- **Lint component (L):** `L = max(0, 1 - issues/50)` where `issues` is the number of Ruff findings.
- **Test component (T):** `T = passed / (passed + failed)` from pytest results.
- **Placeholder component (P):** `P = 1 / (1 + placeholders)` where `placeholders` counts TODO/FIXME markers.

The overall score is the average of the three components:

```
score = (L + T + P) / 3
```

This score is stored in `analytics.db` and surfaced at `/dashboard/compliance`.
