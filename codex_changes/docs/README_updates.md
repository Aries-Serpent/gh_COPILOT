# Enterprise Dashboard: Metrics Views (Scaffold)

## Overview
This addendum describes how to wire the generated stubs for the metrics panels:
- compliance
- synchronization
- monitoring

## Real-time Updates
The supplied templates use periodic JSON polling to update Chart.js gauges.
Replace the mock handlers with real metrics and keep the JSON schema stable.

## Tests
- See `codex_changes/tests/test_dashboard_endpoints.py`
- Run: `pytest -q`

## Safety
- This scaffold does not edit your source files automatically.
- Apply the suggested patches manually after review.
- **DO NOT ACTIVATE ANY GitHub Actions files.** This scaffold ignores `.github/workflows/*`.
