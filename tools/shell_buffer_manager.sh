#!/usr/bin/env bash
# Redirect lines exceeding 4KB to overflow files under /tmp/gh_copilot_sessions.
set -euo pipefail

TARGET_DIR="/tmp/gh_copilot_sessions"
mkdir -p "$TARGET_DIR"

while IFS= read -r line; do
  bytes=$(printf '%s' "$line" | wc -c)
  if [ "$bytes" -gt 4096 ]; then
    head_part=$(printf '%s' "$line" | head -c 4096)
    tail_part=$(printf '%s' "$line" | tail -c +4097)
    outfile=$(mktemp "$TARGET_DIR/overflow_XXXXXX.log")
    printf '%s' "$tail_part" > "$outfile"
    printf '%s\n' "$head_part"
    echo "OVERFLOW:$outfile" >&2
  else
    printf '%s\n' "$line"
  fi
done
