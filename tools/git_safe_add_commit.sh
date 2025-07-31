#!/usr/bin/env bash
# Safely commit staged files with optional Git LFS tracking
set -e
ALLOW="${ALLOW_AUTOLFS:-0}"
SIZE_LIMIT=$((50 * 1024 * 1024))

FILES=$(git diff --cached --name-only --diff-filter=ACM)
for f in $FILES; do
  [ -f "$f" ] || continue
  size=$(stat -c%s "$f")
  if file "$f" | grep -q binary || [ "$size" -gt "$SIZE_LIMIT" ]; then
    pattern="*${f##*.}"
    if ! grep -q "${pattern}.*filter=lfs" .gitattributes 2>/dev/null; then
      if [ "$ALLOW" = "1" ]; then
        git lfs install >/dev/null 2>&1 || true
        git lfs track "$pattern"
        git add .gitattributes "$f"
        echo "[LFS] Tracking $pattern"
      else
        echo "ERROR: $f is binary or large. Set ALLOW_AUTOLFS=1 to auto-fix." >&2
        exit 1
      fi
    fi
  fi
done

git commit -m "${1:-auto commit}"
[ "$2" = "--push" ] && git push
printf '\342\234\223 Commit complete\n'
