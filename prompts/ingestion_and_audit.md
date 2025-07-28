# Ingestion & Audit Prompts

## Setup and Ingestion
```
source .venv/bin/activate
export GH_COPILOT_WORKSPACE=/path/to/gh_COPILOT
export GH_COPILOT_BACKUP_ROOT=/external/backups
python scripts/automation/setup_ingest_audit.py
```

## Code Audit and Summary
```
python scripts/intelligent_code_analysis_placeholder_detection --workspace-path "$GH_COPILOT_WORKSPACE" --analytics-db databases/analytics.db --production-db databases/production.db --dashboard-dir dashboard/compliance
```

## Issue Creation Guidance
```
Use the audit summary to open GitHub issues for each missing feature or bug. Include labels like `bug`, `enhancement`, or `security`.
```
