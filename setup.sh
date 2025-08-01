#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="$(cd "$(dirname "$0")" && pwd)"

if [ ! -d "$WORKSPACE/.venv" ]; then
    python3 -m venv "$WORKSPACE/.venv"
fi

source "$WORKSPACE/.venv/bin/activate"

pip install --upgrade pip >/tmp/setup_install.log

pip install -r "$WORKSPACE/requirements.txt" >>/tmp/setup_install.log

python "$WORKSPACE/scripts/setup_environment.py" >>/tmp/setup_install.log

# install clw line wrapper if missing
if [ ! -x /usr/local/bin/clw ]; then
    "$WORKSPACE/tools/install_clw.sh"
fi

/usr/local/bin/clw --help >/dev/null || true

if [ -z "${GH_COPILOT_BACKUP_ROOT:-}" ]; then
    echo "Error: GH_COPILOT_BACKUP_ROOT not set. Please set it to an external backup directory." >&2
    exit 1
fi
export GH_COPILOT_BACKUP_ROOT

echo "Environment initialized. Activate with 'source .venv/bin/activate'"
echo "Set GH_COPILOT_WORKSPACE=$WORKSPACE and GH_COPILOT_BACKUP_ROOT to an external path before running tools."
export GH_COPILOT_WORKSPACE="$WORKSPACE"
