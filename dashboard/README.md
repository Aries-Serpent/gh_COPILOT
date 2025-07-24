# Dashboard

Compliance metrics and summaries.

The `compliance` directory contains generated metrics (`metrics.json`) and correction summaries (`correction_summary.json`).

## `/dashboard/compliance`

This endpoint returns a JSON payload containing real-time metrics and rollback
history pulled from `analytics.db`. The response structure is:

```json
{
  "metrics": {
    "placeholder_removal": 0,
    "compliance_score": 0.0
  },
  "rollbacks": []
}
```
