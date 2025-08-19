#!/usr/bin/env bash
set -euo pipefail

# Run the placeholder audit and capture results for the dashboard and logs.
# Example crontab (runs at 02:30 every day):
# 30 2 * * * /bin/bash /path/to/repo/scripts/run_placeholder_audit.sh \
#   >> /var/log/gh_copilot_placeholder_audit.log 2>&1

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="$ROOT_DIR:${PYTHONPATH:-}"

LOG_DIR="$ROOT_DIR/logs"
mkdir -p "$LOG_DIR"
timestamp="$(date +"%Y%m%d_%H%M%S")"
LOG_FILE="$LOG_DIR/placeholder_audit_$timestamp.log"

python -m scripts.code_placeholder_audit \
  --analytics-db databases/analytics.db \
  --dashboard-dir dashboard/compliance "$@" | tee "$LOG_FILE"

