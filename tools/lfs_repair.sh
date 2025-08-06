#!/usr/bin/env bash
# Repair Git LFS objects by refetching and checking out files.
#
# Usage:
#   tools/lfs_repair.sh [<path>...]
#
# Removes the local LFS object cache, runs `git lfs fetch`,
# `git checkout`, `git lfs checkout`, and `git lfs fsck` to
# verify integrity. Logs all actions to
# "$GH_COPILOT_BACKUP_ROOT/logs/lfs_repair.log".
#
# Environment:
#   GH_COPILOT_BACKUP_ROOT - must point to an external backup directory.
#
set -euo pipefail

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  sed -n '2,12p' "$0"
  exit 0
fi

repo_root="$(git rev-parse --show-toplevel)"

if [[ -z "${GH_COPILOT_BACKUP_ROOT:-}" ]]; then
  echo "GH_COPILOT_BACKUP_ROOT is not set" >&2
  exit 1
fi

case "$GH_COPILOT_BACKUP_ROOT" in
  "$repo_root"* )
    echo "GH_COPILOT_BACKUP_ROOT must be outside the repository" >&2
    exit 1
    ;;
esac

log_dir="$GH_COPILOT_BACKUP_ROOT/logs"
mkdir -p "$log_dir"
log_file="$log_dir/lfs_repair.log"
exec > >(tee -a "$log_file") 2>&1

echo "[$(date -Iseconds)] Starting LFS repair"

echo "Removing local LFS cache..."
rm -rf "$repo_root/.git/lfs/objects"

echo "Fetching LFS objects..."
git lfs fetch --all

if (( $# )); then
  echo "Checking out specified paths: $*"
  git checkout -- "$@"
  git lfs checkout "$@"
else
  echo "Checking out entire repository..."
  git checkout -- .
  git lfs checkout
fi

echo "Verifying integrity..."
git lfs fsck

echo "[$(date -Iseconds)] LFS repair complete"

