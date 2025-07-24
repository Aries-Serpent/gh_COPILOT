# Dashboard

Compliance metrics and summaries.

The `compliance` directory contains generated metrics (`metrics.json`) and correction summaries (`correction_summary.json`).

## `/dashboard/compliance` Endpoint

The Flask dashboard exposes a `/dashboard/compliance` endpoint that returns JSON with:

```json
{
  "metrics": {"placeholder_removal": 0, "compliance_score": 0.0},
  "rollbacks": []
}
```

These values come from `analytics.db` and `dashboard/compliance/correction_summary.json`.
