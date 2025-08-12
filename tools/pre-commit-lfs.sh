#!/usr/bin/env bash
set -euo pipefail

# Ensure Git LFS pointers are valid. Some git-lfs versions do not support
# `--strict`; fall back to a plain listing if the flag is unavailable.
if ! git lfs ls-files --strict >/tmp/lfs_check.log 2>&1; then
  if grep -q "unknown flag" /tmp/lfs_check.log; then
    git lfs ls-files >/dev/null 2>&1 || {
      cat /tmp/lfs_check.log >&2
      exit 1
    }
  else
    cat /tmp/lfs_check.log >&2
    exit 1
  fi
fi

# Collect staged .db files
staged_db_files=$(git diff --cached --name-only -- '*.db')

# Verify each staged .db file is managed by Git LFS
for f in $staged_db_files; do
  if ! git lfs ls-files | grep -Fq " $f"; then
    echo "Error: $f is a .db file not tracked by Git LFS" >&2
    echo "Run 'git lfs track \"*.db\"' and re-add the file." >&2
    exit 1
  fi
done

# Check for untracked .db files in working tree
untracked_db_files=$(git ls-files --others --exclude-standard '*.db')
if [ -n "$untracked_db_files" ]; then
  echo "Error: Untracked .db file(s) found:" >&2
  echo "$untracked_db_files" >&2
  echo "Ensure they are added and tracked by Git LFS." >&2
  exit 1
fi

# Collect staged .zip files
staged_zip_files=$(git diff --cached --name-only -- '*.zip')

# Verify each staged .zip file is managed by Git LFS
for f in $staged_zip_files; do
  if ! git lfs ls-files | grep -Fq " $f"; then
    echo "Error: $f is a .zip file not tracked by Git LFS" >&2
    echo "Run 'git lfs track \"*.zip\"' and re-add the file." >&2
    exit 1
  fi
done

# Check for untracked .zip files in working tree
untracked_zip_files=$(git ls-files --others --exclude-standard '*.zip')
if [ -n "$untracked_zip_files" ]; then
  echo "Error: Untracked .zip file(s) found:" >&2
  echo "$untracked_zip_files" >&2
  echo "Ensure they are added and tracked by Git LFS." >&2
  exit 1
fi

exit 0
