#!/usr/bin/env bash
set -e

# Ensure workspace and backup environment variables are exported
export GH_COPILOT_WORKSPACE="${GH_COPILOT_WORKSPACE:-/app}"
export GH_COPILOT_BACKUP_ROOT="${GH_COPILOT_BACKUP_ROOT:-/backup}"

# Initialize analytics database before launching services
python scripts/database/unified_database_initializer.py

# Start background workers
python dashboard/compliance_metrics_updater.py &

# Launch the Flask dashboard in the foreground
exec python scripts/docker_entrypoint.py
