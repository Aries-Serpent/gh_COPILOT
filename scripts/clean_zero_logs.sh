#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-logs}"

if [ ! -d "$TARGET" ]; then
    echo "Directory '$TARGET' does not exist."
    exit 0
fi

zero_files=$(find "$TARGET" -type f -size 0 ! -path "*/.git/*")

if [ -n "$zero_files" ]; then
    echo "$zero_files" | xargs -r rm -f
    echo "Removed zero-size log files:" >&2
    echo "$zero_files" >&2
else
    echo "No zero-size log files to remove.";
fi
