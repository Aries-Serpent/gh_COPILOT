#!/bin/bash
# shell_buffer_manager.sh
# Hard cutoff and overflow redirection for shell command output.

set -euo pipefail

MAX_LINE_LENGTH=${MAX_LINE_LENGTH:-1550}
TEMP_DIR=${TEMP_DIR:-/tmp/shell_buffer_overflow}
SESSION_ID=${SESSION_ID:-$(date +%s)}
mkdir -p "$TEMP_DIR"

run_and_manage() {
    local cmd="$1"
    local overflow_file="$TEMP_DIR/overflow_${SESSION_ID}.log"
    eval "$cmd" 2>&1 | while IFS= read -r line; do
        local length=${#line}
        if [ "$length" -gt "$MAX_LINE_LENGTH" ]; then
            echo "${line:0:$MAX_LINE_LENGTH}"
            echo "[OVERFLOW] Line truncated at $MAX_LINE_LENGTH chars. Full content: $overflow_file" >&2
            echo "$line" >> "$overflow_file"
        else
            echo "$line"
        fi
    done
}

if [ "$#" -gt 0 ]; then
    run_and_manage "$*"
else
    while IFS= read -r line; do
        length=${#line}
        if [ "$length" -gt "$MAX_LINE_LENGTH" ]; then
            echo "${line:0:$MAX_LINE_LENGTH}"
            echo "[OVERFLOW] Line truncated at $MAX_LINE_LENGTH chars." >&2
        else
            echo "$line"
        fi
    done
fi

