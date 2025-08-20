#!/usr/bin/env bash
set -euo pipefail

rm -rf dist build
find . -maxdepth 1 -name "*.egg-info" -exec rm -rf {} +
