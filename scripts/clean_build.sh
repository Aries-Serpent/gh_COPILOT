#!/usr/bin/env bash
set -euo pipefail

# Always run from repository root
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

rm -rf dist build
find . -maxdepth 1 -name "*.egg-info" -exec rm -rf {} +
