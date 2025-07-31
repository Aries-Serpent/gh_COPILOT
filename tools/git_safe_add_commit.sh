#!/usr/bin/env bash
set -e

SIZE_LIMIT=$((50*1024*1024))
ALLOW="${ALLOW_AUTOLFS:-0}"

FILES=$(git diff --cached --name-only --diff-filter=ACM)

for f in $FILES; do
  [ -f "$f" ] || continue
  if file "$f" | grep -q binary || [ $(wc -c <"$f") -gt "$SIZE_LIMIT" ]; then
    if ! git check-attr filter -- "$f" | grep -q lfs; then
      if [ "$ALLOW" -eq 1 ]; then
        ext="${f##*.}"
        git lfs install
        git lfs track "*.${ext}"
        git add .gitattributes "$f"
        echo "[LFS] Tracking *.${ext}"
      else
        echo "ERROR: $f is binary or large. Set ALLOW_AUTOLFS=1 to auto-fix." >&2
        exit 1
      fi
    fi
  fi
done

git commit -m "${1:-auto commit}"
if [ "$2" = "--push" ]; then
  git push
fi

echo "Commit complete"
