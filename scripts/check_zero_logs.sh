#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="${1:-logs}"

if [ ! -d "$LOG_DIR" ]; then
    echo "Directory '$LOG_DIR' does not exist. Nothing to check."
    exit 0
fi

zero=$(find "$LOG_DIR" -type f -size 0)
if [ -n "$zero" ]; then
    echo "Zero-size log files found:" >&2
    echo "$zero" >&2
    exit 1
fi

echo "No zero-size log files.";
