#!/usr/bin/env bash
# shellcheck disable=SC2016

# Safe ripgrep wrapper with output throttling and diagnostics.
# - Limits columns to prevent exceedingly long lines.
# - Excludes heavy directories.
# - Captures full results to a temp file when truncated.

set -euo pipefail

MAX_COUNT=${SAFE_RG_MAX_COUNT:-200}
BACKUP_ROOT=${GH_COPILOT_BACKUP_ROOT:-/tmp}
TMP_FILE="$(mktemp "${BACKUP_ROOT%/}/safe_rg.XXXXXX.log")"

rg --max-columns=300 --no-messages \
  --max-count=$((MAX_COUNT+1)) \
  --glob '!:builds/**' --glob '!:artifacts/**' --glob '!:archive/**' --glob '!:logs/**' \
  "$@" >"$TMP_FILE" || true

TOTAL_LINES=$(wc -l <"$TMP_FILE")

set +o pipefail
head -n "$MAX_COUNT" "$TMP_FILE" | cut -c1-300
set -o pipefail

if [ "$TOTAL_LINES" -gt "$MAX_COUNT" ]; then
  echo "Result truncated to ${MAX_COUNT} lines. Full output saved to $TMP_FILE" >&2
else
  rm -f "$TMP_FILE"
fi

exit 0

