# Deploy Scripts

This directory contains deployment utilities for the gh_COPILOT dashboard.

## Dashboard Deployment

Use `dashboard_deploy.sh` to build the dashboard image, run database migrations, start services, and perform smoke tests.

```bash
bash deploy/dashboard_deploy.sh staging
```

The script sources WebSocket settings from `dashboard/websocket.env` and checks both the HTTP endpoint and WebSocket port during smoke tests.
