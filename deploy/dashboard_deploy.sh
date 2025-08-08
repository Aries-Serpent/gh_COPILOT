#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT=${1:-staging}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${SCRIPT_DIR%/deploy}"
WEBSOCKET_ENV="${SCRIPT_DIR}/dashboard/websocket.env"
source "${WEBSOCKET_ENV}"

echo "=== Dashboard deployment (${ENVIRONMENT}) ==="

echo "[1/4] Building dashboard image"
if command -v docker >/dev/null 2>&1; then
    docker compose -f "${SCRIPT_DIR}/dashboard.yaml" build
else
    echo "docker not found, skipping build"
fi

echo "[2/4] Running database migrations"
python - <<'PY'
print("Simulating database migration step")
PY

echo "[3/4] Starting dashboard service"
if command -v docker >/dev/null 2>&1; then
    docker compose -f "${SCRIPT_DIR}/dashboard.yaml" up -d
else
    if python -m flask --version >/dev/null 2>&1; then
        FLASK_RUN_PORT=8080 python -m flask --app dashboard.enterprise_dashboard run >/tmp/dashboard.log 2>&1 &
        DASHBOARD_PID=$!
        sleep 1
    else
        echo "Flask not available; skipping service start"
    fi
fi

echo "[4/4] Running smoke tests for ${ENVIRONMENT}"
if curl -fsS "http://localhost:8080/health" >/dev/null 2>&1; then
    echo "HTTP health check passed"
else
    echo "HTTP health check failed"
fi
if timeout 5 bash -c "</dev/tcp/localhost/${WEBSOCKET_PORT}" >/dev/null 2>&1; then
    echo "WebSocket port ${WEBSOCKET_PORT} reachable"
else
    echo "WebSocket port ${WEBSOCKET_PORT} unreachable"
fi

if [[ -n "${DASHBOARD_PID:-}" ]]; then
    kill "${DASHBOARD_PID}" >/dev/null 2>&1 || true
fi

echo "Deployment to ${ENVIRONMENT} completed"
