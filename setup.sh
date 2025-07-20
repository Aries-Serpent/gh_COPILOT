#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="$(cd "$(dirname "$0")" && pwd)"

if [ ! -d "$WORKSPACE/.venv" ]; then
    python3 -m venv "$WORKSPACE/.venv"
fi

source "$WORKSPACE/.venv/bin/activate"

pip install --upgrade pip >/tmp/setup_install.log

pip install -r "$WORKSPACE/requirements.txt" >>/tmp/setup_install.log
if [ -f "$WORKSPACE/requirements-test.txt" ]; then
    pip install -r "$WORKSPACE/requirements-test.txt" >>/tmp/setup_install.log
fi

if [ -z "${GH_COPILOT_BACKUP_ROOT:-}" ]; then
    echo "GH_COPILOT_BACKUP_ROOT not set. Please set it outside the workspace." >&2
fi

echo "Environment initialized. Activate with 'source .venv/bin/activate'"
echo "Set GH_COPILOT_WORKSPACE=$WORKSPACE and GH_COPILOT_BACKUP_ROOT to an external path before running tools."
