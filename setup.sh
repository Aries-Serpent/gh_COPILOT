#!/usr/bin/env bash
set -euo pipefail

WITH_A=0
WITH_TEST=0
WITH_QUANTUM=0
for arg in "$@"; do
    case "$arg" in
        --with-a) WITH_A=1 ;;
        --with-test) WITH_TEST=1 ;;
        --with-quantum) WITH_QUANTUM=1 ;;
        --with-optional|--with-all)
            WITH_A=1
            WITH_TEST=1
            WITH_QUANTUM=1
            ;;
        *)
            echo "Usage: $0 [--with-a] [--with-test] [--with-quantum] [--with-all]" >&2
            exit 1
            ;;
    esac
done

WORKSPACE="$(cd "$(dirname "$0")" && pwd)"

if [ ! -d "$WORKSPACE/.venv" ]; then
    python3 -m venv "$WORKSPACE/.venv"
fi

source "$WORKSPACE/.venv/bin/activate"

pip install --upgrade pip >/tmp/setup_install.log

pip install -r "$WORKSPACE/requirements.txt" >>/tmp/setup_install.log

if [ "$WITH_A" -eq 1 ] && [ -f "$WORKSPACE/requirements-a.txt" ]; then
    pip install -r "$WORKSPACE/requirements-a.txt" >>/tmp/setup_install.log
fi

if [ "$WITH_TEST" -eq 1 ] && [ -f "$WORKSPACE/requirements-test.txt" ]; then
    pip install -r "$WORKSPACE/requirements-test.txt" >>/tmp/setup_install.log
fi

if [ "$WITH_QUANTUM" -eq 1 ] && [ -f "$WORKSPACE/requirements-quantum.txt" ]; then
    pip install -r "$WORKSPACE/requirements-quantum.txt" >>/tmp/setup_install.log
fi

if [ "$WITH_TEST" -eq 1 ]; then
    python -m scripts.setup_environment --install-tests >>/tmp/setup_install.log
else
    python -m scripts.setup_environment >>/tmp/setup_install.log
fi

python scripts/run_migrations.py >>/tmp/setup_install.log

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
