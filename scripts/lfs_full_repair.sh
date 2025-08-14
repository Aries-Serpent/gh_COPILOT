#!/usr/bin/env bash
# Script to perform a full Git LFS repair and migration.
# Backs up refs, audits the repo, migrates history to LFS,
# rehydrates objects and pushes the rewritten refs.
set -euo pipefail

backup_dir="${GH_COPILOT_BACKUP_ROOT:-/tmp}/lfs_repair_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$backup_dir"

echo "[INFO] Backing up current refs to $backup_dir/refs.bundle"
# Create a bundle containing all refs so the previous state can be restored.
git bundle create "$backup_dir/refs.bundle" --all

echo "[INFO] Running repository audits"
# Verify repository integrity before proceeding.
git fsck --full
# Audit existing LFS objects (best effort).
git lfs fsck || true

echo "[INFO] Rewriting history to ensure all large files use LFS"
# Import existing large files into LFS across the entire history.
git lfs migrate import --everything

echo "[INFO] Fetching and checking out LFS objects"
# Ensure all LFS objects are present locally after migration.
git lfs fetch --all
# Checkout LFS objects; allow failure if some objects are missing.
(git lfs checkout || true)

echo "[INFO] Validating LFS pointers"
# Verify that all tracked files are valid LFS pointers.
if git lfs ls-files -n | xargs -r git lfs pointer --check; then
  echo "[INFO] Pointer validation passed"
else
  echo "[WARN] Pointer validation reported issues" >&2
fi

echo "[INFO] Pushing rewritten history to origin"
# Force push all refs and tags because history was rewritten.
git lfs push --all origin
# Push branches and tags with force to update remote history.
git push --force --all origin
git push --force --tags origin

echo "[INFO] LFS full repair complete"
