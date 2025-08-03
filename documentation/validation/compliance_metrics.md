# Compliance Metrics

The compliance report combines linting and test results into a single
**composite compliance score** that ranges from 0 to 100.

## Metric Formulas

- **Lint Score** = `max(0, 100 - ruff_issues)`
- **Test Score** = `(tests_passed / (tests_passed + tests_failed)) * 100` if any
  tests were executed, otherwise `0`.
- **Composite Compliance Score** = `(Lint Score + Test Score) / 2`

The composite score is stored in `databases/analytics.db` alongside the raw
metrics and is surfaced in the Enterprise Dashboard for visibility.

