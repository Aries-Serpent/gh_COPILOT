#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

# ==== Config (patterns fixed by requirement) ====
INCLUDE_PATTERNS="*.zip,*.db"

# ==== Helpers ====
die() { echo "ERROR: $*" >&2; exit 1; }
note() { echo "[INFO] $*"; }
warn() { echo "[WARN] $*" >&2; }

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"
}

timestamp() { date +"%Y%m%d%H%M%S"; }

repo_root() {
  git rev-parse --show-toplevel 2>/dev/null || die "Not inside a Git repo."
}

# ==== Preflight ====
require_cmd git
require_cmd git-lfs

note "git: $(git --version)"
note "git-lfs: $(git lfs version || true)"

ROOT="$(repo_root)"
cd "$ROOT"

# Working tree must be clean
if ! git diff --quiet || ! git diff --cached --quiet; then
  die "Working tree is not clean. Commit or stash changes first."
fi

# Identify remote & default branch
REMOTE="${REMOTE:-origin}"
if ! git remote get-url "$REMOTE" >/dev/null 2>&1; then
  die "Remote '$REMOTE' not found. Set REMOTE env var or add a remote named 'origin'."
fi
REMOTE_URL="$(git remote get-url "$REMOTE")"
DEFAULT_BRANCH="$(git symbolic-ref --short refs/remotes/$REMOTE/HEAD 2>/dev/null | sed "s#^$REMOTE/##" || true)"
if [[ -z "${DEFAULT_BRANCH}" ]]; then
  # Fallback to current branch
  DEFAULT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
fi

note "Repository root: $ROOT"
note "Remote: $REMOTE ($REMOTE_URL)"
note "Default branch: $DEFAULT_BRANCH"

# Paths
ART_DIR="$ROOT/.git/lfs-migration"
mkdir -p "$ART_DIR"
PLAN_LOG="$ART_DIR/plan.log"
INFO_LOG="$ART_DIR/info.log"
MIGRATE_LOG="$ART_DIR/migrate.log"

# Tag & bundle (pre-migration)
TAG="pre-lfs-migration-$(timestamp)"
BUNDLE="../$(basename "$ROOT")-pre-lfs.bundle"

# Record plan
{
  echo "Plan @ $(date -Iseconds)"
  echo " - Include patterns: $INCLUDE_PATTERNS"
  echo " - Remote: $REMOTE ($REMOTE_URL)"
  echo " - Default branch: $DEFAULT_BRANCH"
  echo " - Tag to create: $TAG"
  echo " - Bundle path: $BUNDLE"
} | tee "$PLAN_LOG"

# Ensure LFS installed and tracking rules exist
note "Installing/updating Git LFS filters…"
git lfs install

ATTR_CHANGED=0
if ! grep -qE '^\*\.zip\b' .gitattributes 2>/dev/null; then
  echo '*.zip filter=lfs diff=lfs merge=lfs -text' >> .gitattributes
  ATTR_CHANGED=1
fi
if ! grep -qE '^\*\.db\b' .gitattributes 2>/dev/null; then
  echo '*.db  filter=lfs diff=lfs merge=lfs -text' >> .gitattributes
  ATTR_CHANGED=1
fi
if [[ $ATTR_CHANGED -eq 1 ]]; then
  git add .gitattributes
  git commit -m "chore(lfs): track *.zip and *.db via Git LFS"
  note ".gitattributes updated and committed."
else
  note ".gitattributes already tracks *.zip and *.db"
fi

# Create pre-migration tag and bundle for rollback
note "Creating pre-migration tag: $TAG"
git tag "$TAG"

note "Creating pre-migration bundle at: $BUNDLE"
git bundle create "$BUNDLE" --all

# Dry information (no rewrite)
note "Collecting migrate info (no rewrite)…"
git lfs migrate info --everything | tee "$INFO_LOG"

# Perform migration (history rewrite across all refs)
note "Running full history migration to LFS… this may take a while."
# shellcheck disable=SC2086
git lfs migrate import --everything --include="$INCLUDE_PATTERNS" | tee "$MIGRATE_LOG"

# Verification
note "Verifying LFS pointers exist for target patterns…"
git lfs ls-files | tee "$ART_DIR/ls-files.txt" >/dev/null
if ! grep -E '\.(zip|db)$' "$ART_DIR/ls-files.txt" >/dev/null; then
  warn "No *.zip/*.db files appear in git lfs ls-files output. Check patterns or repository contents."
fi

note "Running git lfs fsck…"
git lfs fsck

# Show push plan
note "Push plan:"
echo "  - Push all branches: git push $REMOTE --all --force-with-lease"
echo "  - Push all tags:     git push $REMOTE --tags --force-with-lease"

# Consent gate
echo
echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
echo "Type CONFIRM to push rewritten history with --force-with-lease, or anything"
echo "else to ABORT now. Your pre-migration backup is: $BUNDLE ; tag: $TAG"
echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
read -r ANSWER
if [[ "$ANSWER" != "CONFIRM" ]]; then
  echo "ABORTED by user. To rollback later, see instructions below."
  echo
  echo "Rollback (from bundle):"
  echo "  mkdir ../restore && cd ../restore"
  echo "  git clone \"$BUNDLE\" restored-repo"
  echo "  cd restored-repo && git remote add origin \"$REMOTE_URL\""
  echo "  # Coordinate with your team before force-pushing the pre-migration state."
  exit 0
fi

# Push rewritten refs
note "Pushing all branches with --force-with-lease…"
git push "$REMOTE" --all --force-with-lease
note "Pushing all tags with --force-with-lease…"
git push "$REMOTE" --tags --force-with-lease

# Post-migration checklist
cat <<'POST'
===============================================================================
Post-Migration Checklist
1) Protect branches: verify branch protections after rewrite.
2) Fresh clone test (recommended):
     GIT_LFS_SKIP_SMUDGE=1 git clone --filter=blob:none <repo-url> test-clone
     cd test-clone && git lfs pull
3) Verify LFS content availability:
     git lfs ls-files | wc -l
     git lfs fsck
4) Inform collaborators to rebase or reclone due to history rewrite.
5) Keep backup bundle safe: ../<repo-name>-pre-lfs.bundle
===============================================================================
POST

note "Migration completed successfully."
