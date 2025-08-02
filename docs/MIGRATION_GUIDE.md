# Migration Guide

This guide highlights recent structural changes and how to adapt existing workflows.

## Renamed Modules
- `scripts/session_wrap_up_engine.py` → `scripts/orchestrators/unified_wrapup_orchestrator.py`

## New Paths
- Runtime artifacts now reside under `artifacts/`:
  - `artifacts/builds/`
  - `artifacts/logs/`
  - `artifacts/results/`
  - `artifacts/reports/`

## Wrap-Up Enforcement
Always invoke `scripts/wlc_session_manager.py` at the end of long-running workflows. The manager logs wrap-up details to `databases/production.db`, stores a local log in `artifacts/logs/`, and mirrors the log to `$GH_COPILOT_BACKUP_ROOT/logs`.

