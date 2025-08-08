#!/bin/bash
# shell_output_manager.sh
# Truncate lines exceeding a safe length to avoid terminal overflows.

MAX_LINE_LENGTH=4000
TEMP_DIR="/tmp/shell_session_overflow"
SESSION_ID=$(date +%s)

safe_execute() {
    local command="$1"
    local temp_file="${TEMP_DIR}/overflow_${SESSION_ID}.log"

    mkdir -p "$TEMP_DIR"

    # Execute with line length monitoring
    $command 2>&1 | while IFS= read -r line; do
        line_length=${#line}
        if [ "$line_length" -gt "$MAX_LINE_LENGTH" ]; then
            # Truncate and redirect overflow
            echo "${line:0:$MAX_LINE_LENGTH}" >&1
            echo "[OVERFLOW] Line truncated at $MAX_LINE_LENGTH chars. Full content: $temp_file" >&1
            echo "$line" >> "$temp_file"
        else
            echo "$line" >&1
        fi
    done
}

