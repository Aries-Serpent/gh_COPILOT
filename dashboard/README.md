# Dashboard

Compliance metrics and summaries are available via the Flask app.

The `/dashboard/compliance` endpoint returns JSON data with metrics and recent rollbacks. Metrics are generated from `analytics.db` and stored in the `dashboard/compliance` directory as `metrics.json` and `correction_summary.json`.
