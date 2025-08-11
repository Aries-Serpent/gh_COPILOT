#!/usr/bin/env bash
set -euo pipefail

# Wrapper around ripgrep enforcing sane defaults to avoid runaway line sizes.
exec rg --max-columns=200 --max-columns-preview "$@"

