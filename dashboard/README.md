# DASHBOARD MODULE: ENTERPRISE MONITORING AND COMPLIANCE  
> Generated: 2025-07-24 19:18:55 | Author: mbaetiong

## OVERVIEW

The Enterprise Dashboard module is the central observability and control interface for the gh_COPILOT toolkit. It enables real-time monitoring of core system operations, session management, compliance reporting, and database orchestration—all in a unified web GUI built with Flask and Jinja2.

This module is designed to meet enterprise auditability and compliance standards, providing a single-pane-of-glass for operational health, process compliance, backup management, and DUAL COPILOT validation. All dashboard operations are tracked and validated for compliance, with full audit trails and rollback capabilities.

---

## Setup

1. Run `bash setup.sh` to install dependencies. If the script reports an error, ensure required system packages and Python
   dependencies are installed.
2. Activate the virtual environment:
   `source .venv/bin/activate`.
3. Launch the dashboard with `python dashboard/enterprise_dashboard.py`.

---

## FEATURES

| Feature                      | Description                                                                                  |
|------------------------------|----------------------------------------------------------------------------------------------|
| Real-Time Metrics            | Live system performance, usage, and health status                                            |
| Session Management           | Track, control, and validate current and historical sessions                                |
| Database Operations          | Manage, browse, and synchronize all enterprise databases (production, analytics, monitoring) |
| Compliance Reporting         | Visualizes DUAL COPILOT validation, compliance status, audit/rollback history               |
| Compliance Score Visualization | Real-time Chart.js graphs with L/T/P gauges and CSV/JSON export options |
| Backup and Recovery          | Initiate enterprise backup jobs, view logs, run restores, manage backup retention           |
| Visual Processing Indicators | Progress bars, phase indicators, detailed execution status                                   |
| Quantum Monitoring           | Extensible hooks for quantum and advanced analytics                                         |
| Monitoring Integration       | Pushes compliance metrics to unified monitoring and correction systems for remediation      |

---

## ARCHITECTURE

- **Backend:** Flask application (`dashboard/enterprise_dashboard.py` wraps
  `web_gui.scripts.flask_apps.enterprise_dashboard`)
- **Templates:** Jinja2 HTML (`dashboard/templates/`)
- **Static Content:** CSS, JS, images (`dashboard/static/`)
- **Correction Log UI:** Vue component (`web/dashboard/components/CorrectionLog.vue`) fetches
  `/corrections/logs` and supports client-side filtering and pagination. Real-time
  updates arrive via `/ws/corrections` with automatic SSE fallback handled by
  `dashboard/static/js/corrections_ws_listener.js`.
- **Data Sources:** `production.db`, `analytics.db`, `monitoring.db`
- **Primary Endpoints:** `/`, `/database`, `/backup`, `/migration`, `/deployment`, `/api/scripts`, `/api/health`, `/metrics_stream`, `/corrections_stream`, `/ws/corrections`, `/dashboard/compliance`
- **Session Logging:** All actions are recorded in `production.db` and mirrored in `analytics.db`
- **Compliance Display:** DUAL COPILOT validation and compliance events visible in dashboard sidebar and `/dashboard/compliance`

---

## ENVIRONMENT VARIABLES

| Variable                   | Used For                                                  |
|----------------------------|----------------------------------------------------------|
| `GH_COPILOT_WORKSPACE`     | Sets the workspace root for all dashboard operations     |
| `GH_COPILOT_BACKUP_ROOT`   | Location for backup files and dashboard logs             |
| `FLASK_ENV`                | Set to `development` for Flask debug mode                |

---

## Metric Sources and Tooltips

Metrics shown in the dashboard are queried from `/api/compliance_scores`,
which reads composite and component scores from `analytics.db`. The
frontend updates the `title` attribute for each metric, enabling native
browser tooltips with definitions and timestamps. Clicking a gauge
reveals these descriptions in an inline panel for quick drill-down.

---

## MODULE DIRECTORY STRUCTURE

```
dashboard/
├── enterprise_dashboard.py       # Flask app main entrypoint
├── templates/
│   ├── dashboard.html            # Main dashboard view
│   ├── compliance.html           # Compliance and audit report pages
│   └── ...                      # Additional Jinja2 templates
├── static/
│   ├── css/                     # Stylesheets
│   ├── js/                      # JavaScript assets
│   └── ...                      # Images, icons, etc.
├── compliance/
│   ├── metrics.json             # Generated aggregated metrics
│   ├── correction_summary.json  # Summaries of compliance corrections and rollbacks
└── README.md                    # This documentation
```

---

## USAGE

### Starting the Dashboard

```bash
python dashboard/enterprise_dashboard.py  # wrapper for web_gui Flask app
```

Visit [http://localhost:5000](http://localhost:5000) in your browser. The dashboard will auto-discover and display current session, database, and compliance data. All metrics update in real time.
The dashboard HTML template lives in `dashboard/templates/dashboard.html` and automatically refreshes metrics via Server-Sent Events. If SSE is not supported, a JavaScript fallback polls `/dashboard/compliance` every five seconds.

Example screenshot:

![Dashboard Screenshot](static/dashboard_screenshot.png)

### Manual QA

1. Start the dashboard: `python dashboard/enterprise_dashboard.py`.
2. Visit [http://localhost:5000/](http://localhost:5000/) and verify the dashboard renders.
3. Open `/overview` to view metrics, rollback logs, sync events, and audit results together.
4. Open `/metrics/view` to confirm metrics are displayed.
5. Open `/rollback-logs/view` to confirm rollback entries are shown.
6. Open `/sync-events/view` to confirm synchronization events are shown.
7. Ensure styling from `dashboard/static/style.css` is applied.

### Live Metrics

The dashboard templates consume `/metrics_stream` and `/corrections_stream` via
Server-Sent Events (SSE). Metrics and correction logs are retrieved from
`analytics.db`. If SSE is unavailable, a JavaScript fallback polls
`/dashboard/compliance` and `/corrections` every five seconds. Alerts combine
rollback and violation logs so operators can react to compliance issues
immediately.

### Real-Time Corrections

`CorrectionLog.vue` relies on `dashboard/static/js/corrections_ws_listener.js`
to stream updates from `/ws/corrections`. If the WebSocket connection fails,
the listener automatically falls back to Server-Sent Events from
`/corrections_stream`, ensuring the log remains current.

---

## ENDPOINTS

| Endpoint                  | Functionality                                                                    |
|---------------------------|----------------------------------------------------------------------------------|
| `/`                       | Executive dashboard: live metrics, session overview, compliance                  |
| `/database`               | Database browser, management, and sync controls                                  |
| `/backup`                 | Backup and restore tools, log viewer                                            |
| `/migration`              | Database and session migration operations                                        |
| `/deployment`             | Deployment status and controls                                                   |
| `/api/scripts`            | Run and monitor scripts via API                                                  |
| `/api/health`             | System health check API                                                          |
| `/metrics_stream`         | Server-Sent Events stream of live metrics                                       |
| `/corrections_stream`     | SSE stream of recent correction logs                                            |
| `/ws/corrections`         | WebSocket stream of correction logs (SSE fallback)                              |
| `/dashboard/compliance`   | Returns compliance metrics, rollback and audit trail as JSON                     |
| `/overview`               | Consolidated dashboard with metrics, rollbacks, sync events, and audit results   |
#### Example `/dashboard/compliance` Response

The `/dashboard/compliance` endpoint returns compliance information as JSON, combining live metrics from `analytics.db` and correction/rollback summaries from `dashboard/compliance/correction_summary.json`.

`metrics.json` uses the following schema (applies to both `dashboard/metrics.json` and `dashboard/compliance/metrics.json`). `compliance_score` values are percentages from 0 to 100:

```json
{
  "metrics": {
    "placeholder_removal": 0,
    "open_placeholders": 0,
    "resolved_placeholders": 0,
    "compliance_score": 0.0,
    "progress": 0.0,
    "violation_count": 0,
    "rollback_count": 0,
    "progress_status": "unknown",
    "last_update": "ISO8601 timestamp"
  },
  "status": "updated",
  "timestamp": "ISO8601 timestamp"
}
```

```json
{
  "metrics": {
    "placeholder_removal": 14,
    "compliance_score": 0.993
  },
  "rollbacks": [
    {
      "timestamp": "2025-07-23T11:32:10Z",
      "event": "Template rollback",
      "details": "Rolled back non-compliant script template"
    }
  ]
}
```

- `metrics` — Aggregated compliance metrics (e.g., placeholder removal count, open and resolved placeholder totals, compliance score, remediation progress); includes `progress_status` to summarize placeholder resolution progress
- `rollbacks` — List of correction and rollback events
- `notes` — Array of status messages using text tags like `[SUCCESS]`

The endpoint is used by the dashboard UI and can be queried by external tools for compliance reporting and audit automation.

### `placeholder_summary.json` Schema

`dashboard/compliance/placeholder_summary.json` contains the latest placeholder audit status. The `compliance_score` is expressed as a percentage from 0 to 100:

```json
{
  "timestamp": "ISO8601 timestamp",
  "findings": 0,
  "resolved_count": 0,
  "compliance_score": 0,
  "progress_status": "issues_pending",
  "compliance_status": "non_compliant",
  "placeholder_counts": {}
}
```

### `correction_summary.json` Schema

`dashboard/compliance/correction_summary.json` lists recent corrections:

```json
{
  "timestamp": "ISO8601 timestamp",
  "total_corrections": 0,
  "corrections": [],
  "status": "complete"
}
```

### `cross_reference_summary.json` Schema

`dashboard/compliance/cross_reference_summary.json` records cross-link actions and recommendations:

```json
{
  "timestamp": "ISO8601 timestamp",
  "cross_linked_actions": [],
  "cross_links": [],
  "suggested_links": [],
  "recommended_links": [],
  "status": "complete"
}
```

---

## COMPLIANCE INTEGRATION

- All dashboard logic is validated and logged for enterprise compliance via DUAL COPILOT pattern
- Visual indicators (progress, phase, validation) are displayed in real time
- All audit events and rollbacks are timestamped and associated with active user sessions
- Compliance metrics are written to `analytics.db`, correction summaries to `dashboard/compliance/correction_summary.json`

---

## VISUAL PROCESSING

- Progress bars indicate the state of ongoing operations
- Color-coded compliance status: green (compliant), red (violations), yellow (audit pending)
- Phase indicators and timestamps for all long-running jobs
- Completion summaries and audit trail available in sidebar and compliance pages

---

## EXTENSION AND CUSTOMIZATION

- New endpoints can be added via Flask blueprints in `enterprise_dashboard.py`
- Additional data sources can be integrated by updating dashboard context loaders and data connectors
- To display new compliance/audit metrics, extend sidebar modules in `templates/dashboard.html`
- All new features must implement anti-recursion validation and update the compliance audit trail

---

## TROUBLESHOOTING

- If the dashboard does not display properly:
  - Check that `production.db`, `analytics.db`, and `monitoring.db` exist in the workspace root
  - Verify all required environment variables are set before launch
  - For verbose debug output, run with `FLASK_ENV=development`
- For compliance or audit errors, consult `dashboard/compliance/correction_summary.json` and `analytics.db`

---

## RELATED DOCUMENTATION

- [Repository Guidelines](../docs/REPOSITORY_GUIDELINES.md)
- [WLC Session Manager](../docs/WLC_SESSION_MANAGER.md)
- [Enterprise Context Guide](../.github/instructions/ENTERPRISE_CONTEXT.instructions.md)
- [DUAL COPILOT Pattern](../.github/instructions/DUAL_COPILOT_PATTERN.instructions.md)

---

## MAINTAINER NOTES

- All dashboard code must run anti-recursion validation before file/database operations
- New features require updates to this README and corresponding compliance tests
- All dashboard-related PRs must pass validation via `scripts/validation/enterprise_dual_copilot_validator.py`
- Keep `compliance/metrics.json` and `correction_summary.json` up to date with each release

---
