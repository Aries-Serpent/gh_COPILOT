#!/usr/bin/env bash
set -euo pipefail

terminate() {
    echo "Received termination signal. Stopping children..." >&2
    kill $(jobs -p) 2>/dev/null || true
}

trap terminate INT TERM

# Validate enterprise environment before starting services
python - <<'PY'
from utils.validation_utils import validate_enterprise_environment
validate_enterprise_environment()
PY

# Ensure workspace and backup environment variables are exported
export GH_COPILOT_WORKSPACE="${GH_COPILOT_WORKSPACE:-/app}"
export GH_COPILOT_BACKUP_ROOT="${GH_COPILOT_BACKUP_ROOT:-/backup}"
# Verify Flask secret key is provided for dashboard security
: "${FLASK_SECRET_KEY:?FLASK_SECRET_KEY not set}"

# Initialize analytics database before launching services
python scripts/database/unified_database_initializer.py

# Start background workers
python dashboard/compliance_metrics_updater.py &
metrics_pid=$!

python scripts/code_placeholder_audit.py &
audit_pid=$!

python scripts/docker_entrypoint.py &
dashboard_pid=$!

# Wait for child processes to exit and log errors
wait $metrics_pid
status=$?
if [ $status -ne 0 ]; then
    echo "compliance_metrics_updater exited with status $status" >&2
fi

wait $audit_pid
status=$?
if [ $status -ne 0 ]; then
    echo "code_placeholder_audit exited with status $status" >&2
fi

wait $dashboard_pid
status=$?
if [ $status -ne 0 ]; then
    echo "docker_entrypoint exited with status $status" >&2
fi
