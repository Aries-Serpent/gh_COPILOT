#!/usr/bin/env bash
set -euo pipefail

cleanup() {
    echo "Received termination signal. Stopping children..." >&2
    kill $(jobs -p) 2>/dev/null || true
    python scripts/wlc_session_manager.py || true
}

trap cleanup INT TERM EXIT

# Validate enterprise environment before starting services
python - <<'PY'
from utils.validation_utils import validate_enterprise_environment
validate_enterprise_environment()
PY

# Ensure required environment variables are present
: "${GH_COPILOT_WORKSPACE:?GH_COPILOT_WORKSPACE is not set}"
: "${GH_COPILOT_BACKUP_ROOT:?GH_COPILOT_BACKUP_ROOT is not set}"
: "${FLASK_SECRET_KEY:?FLASK_SECRET_KEY not set}"

export GH_COPILOT_WORKSPACE
export GH_COPILOT_BACKUP_ROOT

# Initialize the enterprise assets database if it doesn't exist
initialize_database_if_missing() {
    local db_path="$GH_COPILOT_WORKSPACE/databases/enterprise_assets.db"
    if [ ! -f "$db_path" ]; then
        python scripts/database/unified_database_initializer.py
    fi
}

initialize_database_if_missing

# Start background workers
python dashboard/compliance_metrics_updater.py &
metrics_pid=$!

python scripts/code_placeholder_audit.py &
audit_pid=$!

exec "$@"
