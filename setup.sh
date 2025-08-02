#!/usr/bin/env bash
set -euo pipefail

WITH_OPTIONAL=0
for arg in "$@"; do
    case "$arg" in
        --with-optional) WITH_OPTIONAL=1 ;;
        *) echo "Usage: $0 [--with-optional]" >&2; exit 1 ;;
    esac
done

WORKSPACE="$(cd "$(dirname "$0")" && pwd)"

if [ ! -d "$WORKSPACE/.venv" ]; then
    python3 -m venv "$WORKSPACE/.venv"
fi

source "$WORKSPACE/.venv/bin/activate"

pip install --upgrade pip >/tmp/setup_install.log

pip install -r "$WORKSPACE/requirements.txt" >>/tmp/setup_install.log

if [ "$WITH_OPTIONAL" -eq 1 ]; then
    for req in "$WORKSPACE/requirements-a.txt" "$WORKSPACE/requirements-test.txt" "$WORKSPACE/requirements-quantum.txt"; do
        if [ -f "$req" ]; then
            pip install -r "$req" >>/tmp/setup_install.log
        fi
    done
fi

python "$WORKSPACE/scripts/setup_environment.py" >>/tmp/setup_install.log
if find "$WORKSPACE/databases/migrations" -name '*.sql' | grep -q .; then
    python "$WORKSPACE/scripts/run_migrations.py" >>/tmp/setup_install.log
fi

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
