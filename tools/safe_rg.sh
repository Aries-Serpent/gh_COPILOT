#!/usr/bin/env bash
set -euo pipefail

# Wrapper around ripgrep with sane defaults.
# - Limits columns to avoid exceedingly long lines.
# - Suppresses error messages.
# - Skips heavy build directories by default.

rg --max-columns=300 --no-messages --glob '!:builds/**' "$@" | cut -c1-300
exit ${PIPESTATUS[0]}

