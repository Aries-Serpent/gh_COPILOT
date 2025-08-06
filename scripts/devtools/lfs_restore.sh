#!/usr/bin/env bash
# lfs_restore.sh - restore a Git LFS-tracked file
#
# Usage: scripts/devtools/lfs_restore.sh [path]
#
# Restores the given Git LFS file (default databases/production.db) by:
#   1. Verifying pointer metadata with git lfs pointer
#   2. Fetching the file via git lfs pull --include
#   3. Rechecking out the file from git
#   4. Validating the file's sha256 checksum against the pointer

set -euo pipefail

FILE_PATH="${1:-databases/production.db}"

# Step 1: ensure file is an LFS pointer
expected_oid=$(git lfs pointer --file "$FILE_PATH" 2>/dev/null | awk '/^oid sha256:/ {print $3}')
if [[ -z "$expected_oid" ]]; then
  echo "Error: $FILE_PATH is not a valid Git LFS pointer" >&2
  exit 1
fi

# Step 2: fetch object via LFS
git lfs pull --include="$FILE_PATH"

# Step 3: re-checkout the file to replace pointer with content
git checkout -- "$FILE_PATH"

# Step 4: verify checksum
actual_oid=$(sha256sum "$FILE_PATH" | awk '{print $1}')
if [[ "$expected_oid" != "$actual_oid" ]]; then
  echo "Checksum mismatch: expected $expected_oid but got $actual_oid" >&2
  exit 1
fi

echo "$FILE_PATH restored and verified."
