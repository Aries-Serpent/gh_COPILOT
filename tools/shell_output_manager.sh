#!/bin/bash
# shell_output_manager.sh
# Truncate lines exceeding a safe length to avoid terminal overflows.

MAX_LINE_LENGTH=4000
TEMP_DIR="/tmp/shell_session_overflow"
SESSION_ID=$(date +%s)

safe_execute() {
    local command="$1"
    local overflow_file="${TEMP_DIR}/overflow_${SESSION_ID}.log"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    local chunk_index=0
    local overflow_count=0

    mkdir -p "$TEMP_DIR"

    echo "[SESSION] timestamp=$timestamp command=\"$command\"" >&2

    while IFS= read -r line; do
        chunk_index=$((chunk_index+1))
        line_length=${#line}
        if [ "$line_length" -gt "$MAX_LINE_LENGTH" ]; then
            # Truncate and redirect overflow
            echo "${line:0:$MAX_LINE_LENGTH}" >&1
            echo "[OVERFLOW] Line truncated at $MAX_LINE_LENGTH chars. Full content: $overflow_file" >&1
            echo "[CHUNK $chunk_index] $line" >> "$overflow_file"
            overflow_count=$((overflow_count+1))
        else
            echo "$line" >&1
        fi
    done < <(eval "$command" 2>&1)

    echo "[SUMMARY] chunks=$chunk_index, truncated=$overflow_count, overflow_file=$overflow_file" >&2
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    if [ "$#" -gt 0 ]; then
        safe_execute "$*"
    fi
fi

