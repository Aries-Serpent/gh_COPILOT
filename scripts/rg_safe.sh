#!/usr/bin/env bash
# Delegate to the central safe ripgrep wrapper.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${SCRIPT_DIR}/../tools/safe_rg.sh" "$@"

