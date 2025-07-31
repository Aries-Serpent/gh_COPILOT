#!/usr/bin/env bash
# Safely commit staged files with optional Git LFS auto-tracking.
set -euo pipefail

ALLOW="${ALLOW_AUTOLFS:-0}"
SIZE_LIMIT=$((50*1024*1024))

files=$(git diff --cached --name-only --diff-filter=ACM)
for f in $files; do
  [ -f "$f" ] || continue
  if file "$f" | grep -q binary || [ $(wc -c <"$f") -gt "$SIZE_LIMIT" ]; then
    if ! git check-attr filter -- "$f" | grep -q lfs; then
      if [ "$ALLOW" = "1" ]; then
        ext="${f##*.}"
        git lfs install
        git lfs track "*.${ext}"
        git add .gitattributes
        git add "$f"
        echo "[LFS] Tracking *.${ext}"
      else
        echo "ERROR: $f is binary or large. Set ALLOW_AUTOLFS=1 to auto-fix." >&2
        exit 1
      fi
    fi
  fi
done

msg=${1:-"auto commit"}
shift || true

git commit -m "$msg"
if [ "$#" -gt 0 ] && [ "$1" = "--push" ]; then
  git push
fi
