# Dashboard

Compliance metrics and summaries.

The `compliance` directory contains generated metrics (`metrics.json`) and correction summaries (`correction_summary.json`).

## Endpoints

The Flask dashboard exposes a compliance endpoint:

* **`/dashboard/compliance`** – returns JSON with:
  * `metrics` – aggregated values from `analytics.db`.
  * `rollbacks` – correction events found in `dashboard/compliance/correction_summary.json`.

Example:

```json
{
  "metrics": {"placeholder_removal": 10, "compliance_score": 0.98},
  "rollbacks": []
}
```
