# Dashboard Setup

This dashboard provides visibility into compliance metrics and rollback history.

## Setup

1. Ensure the virtual environment is activated.
2. Run the Flask app:

```bash
python dashboard/integrated_dashboard.py
```

The application will attempt to read `metrics.json` and `databases/analytics.db`. If the
analytics database is missing, the dashboard will still load with empty metrics and logs.

## Screenshots
Screenshots are stored as base64 text to avoid committing binary files. Recreate them
with the provided CLI and then view the generated images.

```bash
python scripts/restore_dashboard_images.py docs/dashboard/dashboard.b64 docs/dashboard/metrics.b64
```

Once decoded, the images will be written alongside their `.b64` sources:

![Main Dashboard](dashboard.png)

![Metrics View](metrics.png)

