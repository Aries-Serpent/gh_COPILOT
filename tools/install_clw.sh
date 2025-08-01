#!/usr/bin/env bash
# Install or recreate the clw line wrapping utility by copying the canonical script.
set -euo pipefail

SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="/usr/local/bin/clw"
cp "$SRC_DIR/clw.py" "$TARGET"
chmod +x "$TARGET"
echo "clw installed to $TARGET"
