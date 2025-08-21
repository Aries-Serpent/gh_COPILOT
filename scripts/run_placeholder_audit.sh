#!/usr/bin/env bash
set -euo pipefail

# Run the placeholder audit module.
# For scheduling details, see docs/placeholder_audit_guide.md.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python -m scripts.code_placeholder_audit "$@"

