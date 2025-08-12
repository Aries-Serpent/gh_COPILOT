#!/usr/bin/env bash
set -euo pipefail

has() { command -v "$1" >/dev/null 2>&1; }

# Ensure Git LFS is installed
if ! has git-lfs; then
  echo "Installing git-lfs..."
  if has apt-get; then
    apt-get update >/dev/null 2>&1 && apt-get install -y git-lfs >/dev/null 2>&1
  else
    echo "Warning: unable to install git-lfs automatically." >&2
  fi
fi

# Ensure pre-commit is installed
if ! has pre-commit; then
  echo "Installing pre-commit..."
  if has pipx; then
    pipx install pre-commit >/dev/null 2>&1 || true
  elif has pip; then
    pip install pre-commit >/dev/null 2>&1 || true
  else
    echo "Warning: no installer available for pre-commit." >&2
  fi
fi

# Verify pre-commit installation succeeded
if ! has pre-commit; then
  echo "Error: pre-commit is required but could not be installed." >&2
  exit 1
fi

# Initialize Git LFS and pre-commit hooks if available
if has git-lfs; then
  git lfs install --local >/dev/null 2>&1 || true
fi
if has pre-commit; then
  pre-commit install --install-hooks >/dev/null 2>&1 || true
fi
