#!/usr/bin/env bash
set -euo pipefail

# Install or update the clw utility under /usr/local/bin.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC="$REPO_ROOT/tools/clw"
TARGET="/usr/local/bin/clw"

if [ ! -f "$SRC" ]; then
    echo "Source script not found: $SRC" >&2
    exit 1
fi

install -m 0755 "$SRC" "$TARGET"
echo "Installed clw to $TARGET"

