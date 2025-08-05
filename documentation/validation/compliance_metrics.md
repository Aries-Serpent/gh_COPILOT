# Compliance Metrics

The compliance report combines linting, testing, and placeholder resolution
results into a single **composite compliance score** that ranges from 0 to 100.
Anti-recursion checks are enforced separately and must pass before scores are
recorded.

## Metric Formulas

- **Lint Score** = `max(0, 100 - ruff_issues)`
- **Test Score** = `(tests_passed / (tests_passed + tests_failed)) * 100` if any
  tests were executed, otherwise `0`.
- **Placeholder Score** = `(placeholders_resolved / total_placeholders) * 100`
  where `total_placeholders` is the sum of open and resolved placeholders. If no
  placeholders were found the component defaults to `100`.
- **Composite Compliance Score** = `(Lint Score + Test Score + Placeholder Score) / 3`

The composite score is stored in `databases/analytics.db` alongside the raw
metrics and is surfaced in the Enterprise Dashboard for visibility.

