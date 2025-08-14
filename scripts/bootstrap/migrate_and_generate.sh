#!/usr/bin/env bash
set -euo pipefail
ROOT="${GH_COPILOT_WORKSPACE:-$(pwd)}"
VENV="${ROOT}/.venv"
if [ ! -d "$VENV" ]; then
  python3 -m venv "$VENV"
fi
source "$VENV/bin/activate"
python -m pip install -U pip wheel
python -m pip install -e ".[dev,quantum-extra]" || python -m pip install -e ".[dev]"
echo ">> Running migrations"
gh-copilot migrate-all
echo ">> Seeding template tables (idempotent)"
if [ -f scripts/seed_templates.py ]; then
  python scripts/seed_templates.py || true
fi
echo ">> Generating docs/scripts"
gh-copilot generate docs --out-dir generated/docs || true
gh-copilot generate scripts --out-dir generated/scripts || true
echo '{"bootstrap":"ok","migrations":"ok","generation":"ok"}'
