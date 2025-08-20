#!/usr/bin/env bash
set -euo pipefail

# Run the placeholder audit module.
# Example cron job (runs at 02:30 every day):
# 30 2 * * * /bin/bash /path/to/repo/scripts/run_placeholder_audit.sh \
#   >> /var/log/gh_copilot_placeholder_audit.log 2>&1

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python -m scripts.code_placeholder_audit "$@"

