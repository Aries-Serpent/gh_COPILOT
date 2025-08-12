#!/usr/bin/env bash
# Purpose: One-shot bootstrap to apply .gitattributes (LFS rules for archives),
#          install Git LFS + pre-commit, convert existing archives to LFS pointers,
#          and install commit/push hooks. Idempotent and safe for repeated runs.
# Usage:   bash bootstrap_lfs_precommit.sh
# Options: BOOTSTRAP_NO_RUN=1   # skip pre-commit run --all-files
#          DRY_RUN=1            # show actions without changing repo
#          FORCE_COMMIT=1       # commit .gitattributes changes even if no files changed
set -euo pipefail

# -------------- sanity checks --------------
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "❌ Not inside a Git repository. Aborting." >&2
  exit 1
fi

has() { command -v "$1" >/dev/null 2>&1; }

if ! has git; then echo "❌ git not found on PATH" >&2; exit 1; fi
if ! has git-lfs; then echo "❌ git-lfs not found — install Git LFS first" >&2; exit 1; fi

# -------------- config --------------
ROOT_DIR=$(git rev-parse --show-toplevel)
ATTR_FILE="$ROOT_DIR/.gitattributes"
PRECOMMIT_FILE="$ROOT_DIR/.pre-commit-config.yaml"

# LFS patterns (keep in sync with .gitattributes panel)
mapfile -t LFS_PATTERNS < <(cat <<'PAT'
*.[zZ][iI][pP]
*.tar
*.tgz
*.tar.gz
*.tbz2
*.tar.bz2
*.txz
*.tar.xz
*.tzst
*.tar.zst
*.7z
*.rar
*.jar
*.war
*.ear
*.apk
*.ipa
*.nupkg
*.cab
*.iso
PAT
)

# -------------- helper fns --------------
info() { echo "[info] $*"; }
run()  { if [[ "${DRY_RUN:-0}" == "1" ]]; then echo "DRY: $*"; else eval "$*"; fi }

append_gitattributes_block() {
  local marker_begin="# BEGIN LFS ARCHIVES (autogen)"
  local marker_end="# END LFS ARCHIVES (autogen)"
  local need_block=1
  if [[ -f "$ATTR_FILE" ]] && grep -qF "$marker_begin" "$ATTR_FILE"; then
    need_block=0
  fi
  if (( need_block )); then
    info "Applying LFS archive rules to .gitattributes"
    run "cat >> '$ATTR_FILE' <<'EOF'\n$marker_begin\n# ZIP (case-insensitive)\n*.[zZ][iI][pP] filter=lfs diff=lfs merge=lfs -text\n\n# TAR family\n*.tar        filter=lfs diff=lfs merge=lfs -text\n*.tgz        filter=lfs diff=lfs merge=lfs -text\n*.tar.gz     filter=lfs diff=lfs merge=lfs -text\n*.tbz2       filter=lfs diff=lfs merge=lfs -text\n*.tar.bz2    filter=lfs diff=lfs merge=lfs -text\n*.txz        filter=lfs diff=lfs merge=lfs -text\n*.tar.xz     filter=lfs diff=lfs merge=lfs -text\n*.tzst       filter=lfs diff=lfs merge=lfs -text\n*.tar.zst    filter=lfs diff=lfs merge=lfs -text\n\n# Other archive/container formats\n*.7z         filter=lfs diff=lfs merge=lfs -text\n*.rar        filter=lfs diff=lfs merge=lfs -text\n*.jar        filter=lfs diff=lfs merge=lfs -text\n*.war        filter=lfs diff=lfs merge=lfs -text\n*.ear        filter=lfs diff=lfs merge=lfs -text\n*.apk        filter=lfs diff=lfs merge=lfs -text\n*.ipa        filter=lfs diff=lfs merge=lfs -text\n*.nupkg      filter=lfs diff=lfs merge=lfs -text\n*.cab        filter=lfs diff=lfs merge=lfs -text\n*.iso        filter=lfs diff=lfs merge=lfs -text\n$marker_end\nEOF"
  else
    info ".gitattributes already contains LFS archive block"
  fi
}

ensure_precommit_config() {
  if [[ -f "$PRECOMMIT_FILE" ]]; then
    info ".pre-commit-config.yaml already present"
    return
  fi
  info "Writing minimal .pre-commit-config.yaml (LFS + hygiene)"
  run "cat > '$PRECOMMIT_FILE' <<'YAML'\nminimum_pre_commit_version: '3.0.0'\nrepos:\n  - repo: https://github.com/pre-commit/pre-commit-hooks\n    rev: v4.6.0\n    hooks:\n      - id: check-merge-conflict\n      - id: end-of-file-fixer\n      - id: trailing-whitespace\n      - id: check-added-large-files\n        args: ['--maxkb=10000']\n  - repo: local\n    hooks:\n      - id: enforce-zip-lfs\n        name: Enforce Git LFS for ZIP files (*.zip)\n        language: system\n        pass_filenames: false\n        stages: [commit]\n        entry: >-\n          bash -lc 'set -euo pipefail;\n          mapfile -t files < <(git diff --cached --name-only --diff-filter=ACMR | grep -Ei "\\.zip$" || true);\n          [[ ${#files[@]} -eq 0 ]] && exit 0; err=0;\n          for f in "${files[@]}"; do out=$(git check-attr filter -- "$f" 2>/dev/null || true);\n            if [[ "$out" != *": lfs" ]]; then echo "ZIP not LFS-tracked: $f"; err=1; fi; done;\n          ((err)) && exit 1 || exit 0'\nYAML"
}

restage_archives_to_lfs() {
  info "Re-staging existing archives to write LFS pointers (if needed)"
  local changed=0
  for pat in "${LFS_PATTERNS[@]}"; do
    while IFS= read -r -d '' f; do
      [[ -f "$f" ]] || continue
      if ! git check-attr filter -- "$f" | grep -q ': lfs$'; then
        info "Converting to LFS pointer: $f"
        run git rm --cached --quiet -- "$f"
        run git add -- "$f"
        changed=1
      fi
    done < <(git ls-files -z -- "$pat" || true)
  done
  return $changed
}

# -------------- main --------------
info "Installing Git LFS hooks"
run git lfs install

info "Ensuring .gitattributes contains archive rules"
run "mkdir -p '$(dirname "$ATTR_FILE")'"
append_gitattributes_block

info "Adding .gitattributes to index"
run git add .gitattributes

# Convert existing matching files to pointers when necessary
if restage_archives_to_lfs; then
  info "Some archives converted to LFS pointers"
fi

# Commit if there are staged changes
if ! git diff --cached --quiet || [[ "${FORCE_COMMIT:-0}" == "1" ]]; then
  run "git commit -m 'chore(lfs): apply .gitattributes and convert archives to LFS pointers'"
else
  info "No staged changes to commit"
fi

# Ensure pre-commit is installed
if ! has pre-commit; then
  info "Installing pre-commit (pipx or pip --user)"
  if has pipx; then
    run pipx install pre-commit || true
  fi
  if ! has pre-commit; then
    run python3 -m pip install --user pre-commit
    if [[ ":${PATH}:" != *":${HOME}/.local/bin:"* ]] && [[ -d "${HOME}/.local/bin" ]]; then
      export PATH="${HOME}/.local/bin:${PATH}"
    fi
  fi
fi

# Ensure a config exists, then install hooks
ensure_precommit_config
info "Installing pre-commit hooks (commit + pre-push)"
run pre-commit install
run pre-commit install --hook-type pre-push

# Optional: run on all files to catch issues now
if [[ "${BOOTSTRAP_NO_RUN:-0}" != "1" ]]; then
  info "Running pre-commit on all files (first run may take a while)"
  run pre-commit run --all-files || {
    echo "\n⚠️  Pre-commit reported issues. Fix them and re-run your commit." >&2
    exit 1
  }
fi

info "✅ Bootstrap complete — LFS rules applied, archives tracked, hooks installed."
