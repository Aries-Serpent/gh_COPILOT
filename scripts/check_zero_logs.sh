#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-logs}"

if [ ! -d "$TARGET" ]; then
    echo "Directory '$TARGET' does not exist."
    exit 0
fi

zero=$(find "$TARGET" -type f -size 0 ! -path "*/.git/*")
if [ -n "$zero" ]; then
    echo "Zero-size log files found:" >&2
    echo "$zero" >&2
    exit 1
fi

echo "No zero-size log files.";
