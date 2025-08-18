# Monitoring Guide

This guide describes the anomaly detection pipeline provided by
`unified_monitoring_optimization_system`.

## Pipeline Setup

1. Ensure the project virtual environment is active and run `setup.sh`.
2. Metrics are gathered via `collect_metrics` and stored in
   `databases/analytics.db`. Set `LOG_WEBSOCKET_ENABLED=1` to stream updates to
   the dashboard in real time.
 `database_event_monitor` now posts event rate metrics to the dashboard as
  soon as they are recorded.
3. The `anomaly_detection_loop` periodically gathers metrics, evaluates them
   with an `IsolationForest` model, and triggers `auto_heal_session` when
   anomalies are detected.
4. Additional metric sources can register callbacks via
   `register_hook(callable)` which will be invoked during each
   `collect_metrics` cycle.

## Tuning Parameters

- `interval` – seconds between metric collections (default `5`).
- `contamination` – expected proportion of anomalies (default `0.1`).
- `retrain_interval` – frequency the model retrains when using
  `detect_anomalies` directly (default `3600`).
- `model_path` – location of the persisted IsolationForest model
  (`artifacts/anomaly_iforest.pkl`).

Aggregated anomaly counts and average scores are available through
`dashboard.enterprise_dashboard.anomaly_metrics` and appear on the dashboard's monitoring panels for real-time visibility. Set `WEB_DASHBOARD_ENABLED=1` to stream these metrics in real time.

## Dashboard Payload Schema

When `WEB_DASHBOARD_ENABLED=1`, each database event metric emitted by
`database_event_monitor.collect_metrics` is forwarded to the dashboard with the
following JSON structure:

```json
{
  "db_path": "path/to/database.db",
  "event_count": 123
}
```

`db_path` is the path to the monitored database and `event_count` is the total
number of rows currently in `cross_database_sync_operations`.
