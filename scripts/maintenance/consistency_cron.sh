#!/usr/bin/env bash
set -euo pipefail
# Run the auditor daily; suitable for cron or systemd timers.
# Example crontab (runs at 02:17 daily):
# 17 2 * * * /bin/bash /path/to/scripts/maintenance/consistency_cron.sh >> /var/log/gh_copilot_consistency.log 2>&1

ROOT_DIR="$(cd "$(dirname "$0")"/../.. && pwd)"
cd "$ROOT_DIR"
python scripts/database/consistency_auditor.py \
  --enterprise-db enterprise_assets.db \
  --production-db production.db \
  --analytics-db analytics.db \
  --patterns "*.md,*.sql,*.py,*.har" \
  .
