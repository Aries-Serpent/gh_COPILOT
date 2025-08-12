#!/usr/bin/env bash
set -euo pipefail

# Git LFS — Full History Migration (ZIP & DB)
# Rewrites all refs so *.zip and *.db are stored as Git LFS pointers.
# Creates a pre-migration tag + bundle for rollback, verifies results,
# and (optionally) force-pushes with --force-with-lease upon explicit consent.

############################################
# Config
############################################
INCLUDE_PATTERNS="${INCLUDE_PATTERNS:-*.zip,*.db}"  # fixed scope per requirement
REMOTE="${REMOTE:-origin}"                           # override with REMOTE=upstream ./script.sh
ART_DIR_REL=".git/lfs-migration"                    # artifacts inside repo
CONSENT_WORD="${CONSENT_WORD:-CONFIRM}"             # change if you prefer another consent token

############################################
# Helpers
############################################
die()  { echo "ERROR: $*" >&2; exit 1; }
note() { echo "[INFO] $*"; }
warn() { echo "[WARN] $*" >&2; }
ts()   { date +"%Y%m%d%H%M%S"; }

need() {
  command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"
}

repo_root() {
  git rev-parse --show-toplevel 2>/dev/null || die "Not inside a Git repository"
}

symbolic_success_check() {
  # Symbolic condition (documentation only)
  # Success S = T ∧ M ∧ V ∧ P ∧ B, where:
  # T: .gitattributes tracks *.zip, *.db
  # M: git lfs migrate import completed across --everything
  # V: Verification: lfs ls-files and lfs fsck pass
  # P: Rewritten refs pushed w/ --force-with-lease (after consent)
  # B: Backup tag + bundle created before rewrite
  :
}

############################################
# Preflight
############################################
need git
need git-lfs

note "git version     : $(git --version)"
note "git-lfs version : $(git lfs version || true)"

ROOT="$(repo_root)"
cd "$ROOT"

# Ensure clean working tree
if ! git diff --quiet || ! git diff --cached --quiet; then
  die "Working tree not clean. Commit/stash changes and retry."
fi

# Remote + default branch detection
if ! git remote get-url "$REMOTE" >/dev/null 2>&1; then
  die "Remote '$REMOTE' not found. Specify REMOTE=<name> or create a remote named 'origin'."
fi
REMOTE_URL="$(git remote get-url "$REMOTE")"
DEFAULT_BRANCH="$(git symbolic-ref --short "refs/remotes/$REMOTE/HEAD" 2>/dev/null | sed "s#^$REMOTE/##" || true)"
if [[ -z "$DEFAULT_BRANCH" ]]; then
  DEFAULT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
fi

note "Repository root  : $ROOT"
note "Remote           : $REMOTE ($REMOTE_URL)"
note "Default branch   : $DEFAULT_BRANCH"
note "Include patterns : $INCLUDE_PATTERNS"

############################################
# Artifact paths
############################################
ART_DIR="$ROOT/$ART_DIR_REL"
mkdir -p "$ART_DIR"
PLAN_LOG="$ART_DIR/plan.log"
INFO_LOG="$ART_DIR/info.log"
MIGRATE_LOG="$ART_DIR/migrate.log"
LSFILES_LOG="$ART_DIR/ls-files.txt"

TAG="pre-lfs-migration-$(ts)"
BUNDLE="../$(basename "$ROOT")-pre-lfs.bundle"

############################################
# Record Plan
############################################
{
  echo "Plan @ $(date -Iseconds)"
  echo " - Remote: $REMOTE ($REMOTE_URL)"
  echo " - Default branch: $DEFAULT_BRANCH"
  echo " - Include: $INCLUDE_PATTERNS"
  echo " - Pre-migration tag: $TAG"
  echo " - Bundle path: $BUNDLE"
  echo " - Artifacts dir: $ART_DIR_REL"
} | tee "$PLAN_LOG"

############################################
# Ensure LFS filters + tracking rules
############################################
note "Installing/updating Git LFS filters…"
git lfs install

ATTR_CHANGED=0
touch .gitattributes

# Ensure exactly one rule per pattern (idempotent)
if ! grep -qE '^\*\.zip\b.*filter=lfs' .gitattributes; then
  echo '*.zip filter=lfs diff=lfs merge=lfs -text' >> .gitattributes
  ATTR_CHANGED=1
fi
if ! grep -qE '^\*\.db\b.*filter=lfs' .gitattributes; then
  echo '*.db  filter=lfs diff=lfs merge=lfs -text' >> .gitattributes
  ATTR_CHANGED=1
fi

if [[ $ATTR_CHANGED -eq 1 ]]; then
  git add .gitattributes
  git commit -m "chore(lfs): track *.zip and *.db via Git LFS"
  note ".gitattributes updated."
else
  note ".gitattributes already tracks patterns."
fi

############################################
# Safety: pre-migration tag + bundle
############################################
note "Creating pre-migration tag: $TAG"
git tag "$TAG"

note "Creating pre-migration bundle: $BUNDLE"
git bundle create "$BUNDLE" --all

############################################
# Dry Info (no rewrite)
############################################
note "Collecting migrate info across all refs…"
git lfs migrate info --everything | tee "$INFO_LOG"

############################################
# Full History Migration
############################################
note "Running full history migration to LFS for: $INCLUDE_PATTERNS"
# shellcheck disable=SC2086
git lfs migrate import --everything --include="$INCLUDE_PATTERNS" | tee "$MIGRATE_LOG"

############################################
# Verification
############################################
note "Verifying LFS pointers for target extensions…"
git lfs ls-files | tee "$LSFILES_LOG" >/dev/null || true
if ! grep -E '\.(zip|db)$' "$LSFILES_LOG" >/dev/null 2>&1; then
  warn "No *.zip/*.db appear in 'git lfs ls-files'. If your repo truly contains none, this is OK."
fi

note "Running 'git lfs fsck'…"
git lfs fsck

############################################
# Push Plan + Consent Gate
############################################
note "Push plan:"
echo "  - Branches: git push $REMOTE --all --force-with-lease"
echo "  - Tags    : git push $REMOTE --tags --force-with-lease"

echo
echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
echo "Type $CONSENT_WORD to push rewritten history with --force-with-lease,"
echo "or press <Enter> (or anything else) to ABORT now."
echo "Backup bundle: $BUNDLE"
echo "Tag          : $TAG"
echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
read -r ANSWER || true
if [[ "${ANSWER:-}" != "$CONSENT_WORD" ]]; then
  echo "ABORTED by user before push."
  echo
  echo "Rollback (from bundle) if ever needed:"
  echo "  mkdir ../restore && cd ../restore"
  echo "  git clone \"$BUNDLE\" restored-repo"
  echo "  cd restored-repo && git remote add origin \"$REMOTE_URL\""
  echo "  # Coordinate before force-pushing the pre-migration state."
  exit 0
fi

############################################
# Force-with-lease Push (branches + tags)
############################################
note "Pushing all branches…"
git push "$REMOTE" --all --force-with-lease
note "Pushing all tags…"
git push "$REMOTE" --tags --force-with-lease

############################################
# Post-Migration Checklist
############################################
cat <<'POST'
===============================================================================
Post-Migration Checklist
1) Branch protections:
   - Re-validate protected-branch rules after rewrite.

2) Fresh clone test (recommended):
     GIT_LFS_SKIP_SMUDGE=1 git clone --filter=blob:none <repo-url> test-clone
     cd test-clone && git lfs pull

3) Validate LFS content availability:
     git lfs ls-files | wc -l
     git lfs fsck

4) Team coordination:
   - Inform collaborators they must rebase or reclone due to history rewrite.

5) Keep backups:
   - Preserve bundle and tag:
       Bundle: ../<repo-name>-pre-lfs.bundle
       Tag   : pre-lfs-migration-YYYYMMDDHHMMSS
===============================================================================
POST

note "Migration completed successfully."
