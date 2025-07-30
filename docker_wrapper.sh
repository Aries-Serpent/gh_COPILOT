#!/usr/bin/env bash
set -euo pipefail

# Validate required environment variables
: "${GH_COPILOT_WORKSPACE:?GH_COPILOT_WORKSPACE not set}"
: "${GH_COPILOT_BACKUP_ROOT:?GH_COPILOT_BACKUP_ROOT not set}"
: "${FLASK_SECRET_KEY:?FLASK_SECRET_KEY not set}"

python - <<'PY'
from utils.validation_utils import validate_enterprise_environment
validate_enterprise_environment()
PY

python scripts/docker_entrypoint.py &
python dashboard/compliance_metrics_updater.py &
python scripts/code_placeholder_audit.py &

wait
