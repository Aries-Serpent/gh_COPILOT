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

# Ensure Git LFS is installed
if ! has git-lfs; then
  echo "Installing git-lfs..."
  if has apt-get; then
    run "apt-get update >/dev/null 2>&1"
    run "apt-get install -y git-lfs >/dev/null 2>&1"
    if [[ "${DRY_RUN:-0}" == "1" ]]; then
      info "DRY_RUN: would install git-lfs via apt-get"
    fi
  else
    echo "Warning: unable to install git-lfs automatically." >&2
  fi
fi

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
    run "touch '$ATTR_FILE'"
    if [[ -s "$ATTR_FILE" ]]; then
      local last_char
      last_char=$(tail -c1 "$ATTR_FILE" 2>/dev/null || true)
      if [[ "$last_char" != $'\n' ]]; then
        run "printf '\n' >> '$ATTR_FILE'"
      fi
    fi
    run "cat <<'EOF' >> '$ATTR_FILE'"
$marker_begin
# ZIP (case-insensitive)
*.[zZ][iI][pP] filter=lfs diff=lfs merge=lfs -text

# TAR family
*.tar        filter=lfs diff=lfs merge=lfs -text
*.tgz        filter=lfs diff=lfs merge=lfs -text
*.tar.gz     filter=lfs diff=lfs merge=lfs -text
*.tbz2       filter=lfs diff=lfs merge=lfs -text
*.tar.bz2    filter=lfs diff=lfs merge=lfs -text
*.txz        filter=lfs diff=lfs merge=lfs -text
*.tar.xz     filter=lfs diff=lfs merge=lfs -text
*.tzst       filter=lfs diff=lfs merge=lfs -text
*.tar.zst    filter=lfs diff=lfs merge=lfs -text

# Other archive/container formats
*.7z         filter=lfs diff=lfs merge=lfs -text
*.rar        filter=lfs diff=lfs merge=lfs -text
*.jar        filter=lfs diff=lfs merge=lfs -text
*.war        filter=lfs diff=lfs merge=lfs -text
*.ear        filter=lfs diff=lfs merge=lfs -text
*.apk        filter=lfs diff=lfs merge=lfs -text
*.ipa        filter=lfs diff=lfs merge=lfs -text
*.nupkg      filter=lfs diff=lfs merge=lfs -text
*.cab        filter=lfs diff=lfs merge=lfs -text
*.iso        filter=lfs diff=lfs merge=lfs -text
$marker_end
EOF"
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
  run "cat > '$PRECOMMIT_FILE' <<'YAML'
minimum_pre_commit_version: '3.0.0'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: check-merge-conflict
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-added-large-files
        args: ['--maxkb=10000']
  - repo: local
    hooks:
      - id: enforce-zip-lfs
        name: Enforce Git LFS for ZIP files (*.zip)
        language: system
        pass_filenames: false
        stages: [commit]
        entry: >-
          bash -lc 'set -euo pipefail;
          mapfile -t files < <(git diff --cached --name-only --diff-filter=ACMR | grep -Ei \"\\.zip$\" || true);
          [[ \${#files[@]} -eq 0 ]] && exit 0; err=0;
          for f in \"\${files[@]}\"; do out=\$(git check-attr filter -- \"\$f\" 2>/dev/null || true);
            if [[ \"\$out\" != *\": lfs\" ]]; then echo \"ZIP not LFS-tracked: \$f\"; err=1; fi; done;
          ((err)) && exit 1 || exit 0'
YAML"
}

restage_archives_to_lfs() {
  info "Re-staging existing archives to write LFS pointers (if needed)"
  local no_changes=1
  for pat in "${LFS_PATTERNS[@]}"; do
    while IFS= read -r -d '' f; do
      [[ -f "$f" ]] || continue
      if ! git check-attr filter -- "$f" | grep -q ': lfs$'; then
        info "Converting to LFS pointer: $f"
        run git rm --cached --quiet -- "$f"
        run git add -- "$f"
        no_changes=0
      fi
    done < <(git ls-files -z -- "$pat" || true)
  done
  return $no_changes
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

# Ensure a config exists, then install hooks
ensure_precommit_config
info "Installing pre-commit hooks (commit + pre-push)"
run pre-commit install
run pre-commit install --hook-type pre-push

# Optional: run on all files to catch issues now
if [[ "${BOOTSTRAP_NO_RUN:-0}" != "1" ]]; then
  info "Running pre-commit on all files (first run may take a while)"
  run pre-commit run --all-files || {
    echo -e "\n⚠️  Pre-commit reported issues. Fix them and re-run your commit." >&2
    exit 1
  }
fi

info "✅ Bootstrap complete — LFS rules applied, archives tracked, hooks installed."
