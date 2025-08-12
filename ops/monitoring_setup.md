# Monitoring Setup

The monitoring utilities check the uptime of critical services and emit
alerts when failures occur.

## Monitored Services

| Service       | Health Endpoint                  |
|---------------|----------------------------------|
| Sync Engine   | `http://localhost:8000/health`   |
| Dashboard     | `http://localhost:5000/api/health` |
| Anomaly       | `http://localhost:5001/health`   |

## Health Checks

Run `ghc_monitoring.service_health.run_health_checks` to poll the endpoints. Each
result is stored in the `service_uptime` table of `analytics.db` for uptime
analysis.

## Alerting

Failures trigger `critical` alerts via `web_gui.monitoring.alerting.alert_manager`.
The alert pipeline sends notifications to stdout, simulated email, SMS, and the
dashboard.

## Verification

To verify alerts, simulate a failure:

```bash
python - <<'PY'
from ghc_monitoring.service_health import check_service
from web_gui.monitoring.alerting.notification_engine import NOTIFICATION_LOG, EMAIL_LOG, SMS_LOG
check_service("sync_engine", "http://localhost:9/health")
print(NOTIFICATION_LOG[-1])
print(EMAIL_LOG[-1])
print(SMS_LOG[-1])
PY
```

The logs will show the alert dispatched for the unreachable service.

