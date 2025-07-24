#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLW_SRC="$SCRIPT_DIR/clw"
CLW_DST="/usr/local/bin/clw"

if [ ! -f "$CLW_SRC" ]; then
    echo "clw source script not found: $CLW_SRC" >&2
    exit 1
fi

if [ -L "$CLW_DST" ] || [ -f "$CLW_DST" ]; then
    echo "clw already installed at $CLW_DST"
else
    ln -s "$CLW_SRC" "$CLW_DST" 2>/dev/null || cp "$CLW_SRC" "$CLW_DST"
    chmod +x "$CLW_DST"
    echo "Installed clw to $CLW_DST"
fi
