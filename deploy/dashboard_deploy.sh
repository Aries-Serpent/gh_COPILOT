#!/usr/bin/env bash
set -euo pipefail

# Deployment script for the enterprise dashboard
# Handles build, migration, service startup, and smoke testing.

ENVIRONMENT=${1:-staging}
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_DIR="${ROOT_DIR}/deploy/dashboard"

# Load WebSocket configuration
source "${SCRIPT_DIR}/websocket.env"

echo "Deploying dashboard to ${ENVIRONMENT}"

echo "Building dashboard module..."
python -m compileall "${ROOT_DIR}/dashboard" >/dev/null

echo "Applying database migrations..."
sqlite3 "${ROOT_DIR}/databases/analytics.db" < "${ROOT_DIR}/migration_scripts/enterprise_auth_setup.sql"

echo "Starting dashboard service on port ${WEBSOCKET_PORT}"
FLASK_APP=dashboard.integrated_dashboard:create_app \
    FLASK_ENV="${ENVIRONMENT}" \
    flask run --port "${WEBSOCKET_PORT}" >/tmp/dashboard_server.log 2>&1 &
SERVER_PID=$!
# Allow server to start
sleep 3

echo "Running smoke test against http://localhost:${WEBSOCKET_PORT}/metrics"
if curl -fsS "http://localhost:${WEBSOCKET_PORT}/metrics" >/tmp/dashboard_smoke.json; then
    echo "Smoke test passed"
    RESULT=0
else
    echo "Smoke test failed"
    RESULT=1
fi

kill ${SERVER_PID} 2>/dev/null || true
wait ${SERVER_PID} 2>/dev/null || true

# Cleanup temporary artifacts when running in staging
if [[ "${ENVIRONMENT}" == "staging" ]]; then
    rm -f "${ROOT_DIR}/databases/analytics.db"
fi

exit ${RESULT}
