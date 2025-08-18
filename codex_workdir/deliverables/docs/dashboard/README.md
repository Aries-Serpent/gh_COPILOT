# Dashboard Setup

This dashboard provides visibility into compliance metrics and rollback history. Access is secured by a `/login` endpoint that issues session tokens and supports optional MFA before metrics are shown.

## Setup

1. Ensure the virtual environment is activated.
2. Export `LOG_WEBSOCKET_ENABLED=1` to stream live metrics, and set `SYNC_ENGINE_WS_URL` if the sync engine broadcasts over WebSockets.
3. Run the Flask app:

```bash
python dashboard/integrated_dashboard.py
```

With `LOG_WEBSOCKET_ENABLED=1`, synchronization and monitoring panels refresh in real time. The application reads compliance, synchronization, and monitoring data from `databases/analytics.db`. If the analytics database is missing, the dashboard still loads but metrics panels will be empty.

## Screenshots
Screenshots are stored as base64 text to avoid committing binary files. Recreate them
with the provided CLI and then view the generated images.

```bash
python scripts/restore_dashboard_images.py docs/dashboard/dashboard.b64 docs/dashboard/metrics.b64
```

Once decoded, the images will be written alongside their `.b64` sources:

![Main Dashboard](dashboard.png)

![Metrics View](metrics.png)



### Installation
```bash
pip install -r requirements.txt
```

> Note: This project requires `PyYAML>=6.0.1`.
