
#!/usr/bin/env bash
set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI not found. Install GitHub CLI first: https://cli.github.com/"
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "git not found. Please install git."
  exit 1
fi

if [[ $# -lt 6 ]]; then
  cat <<USAGE
Usage: $0 <owner/repo> <branch> <whitepaper.md> <issue.yaml> <pr_title> <pr_body> [--create-issue]
USAGE
  exit 1
fi

REPO="$1"; shift
BRANCH="$1"; shift
WHITEPAPER="$1"; shift
ISSUE_YAML="$1"; shift
PR_TITLE="$1"; shift
PR_BODY="$1"; shift
CREATE_ISSUE="${1-}"

TMP_DIR="$(mktemp -d)"
cleanup() { rm -rf "$TMP_DIR"; }
trap cleanup EXIT

git clone "https://github.com/${REPO}.git" "$TMP_DIR"
cd "$TMP_DIR"
git checkout -b "$BRANCH"

mkdir -p documentation/generated .github/ISSUE_TEMPLATE
cp "$WHITEPAPER" "documentation/generated/$(basename "$WHITEPAPER")"
cp "$ISSUE_YAML" ".github/ISSUE_TEMPLATE/$(basename "$ISSUE_YAML")"

git add -A
git commit -m "$PR_TITLE"
git push --set-upstream origin "$BRANCH"

# PR
gh pr create --title "$PR_TITLE" --body "$PR_BODY" --base master --head "$BRANCH"

# Issue (optional)
if [[ "$CREATE_ISSUE" == "--create-issue" ]]; then
  TITLE=$(python - <<'PY'\nimport yaml,sys\nprint(yaml.safe_load(open(sys.argv[1],'r',encoding='utf-8'))['title'])\nPY\n "$ISSUE_YAML")
  BODY=$(python - <<'PY'\nimport yaml,sys\nprint(yaml.safe_load(open(sys.argv[1],'r',encoding='utf-8'))['description'])\nPY\n "$ISSUE_YAML")
  LABELS=$(python - <<'PY'\nimport yaml,sys,json\nprint(json.dumps(yaml.safe_load(open(sys.argv[1],'r',encoding='utf-8')).get('labels',[])))\nPY\n "$ISSUE_YAML")
  ASSIGNEES=$(python - <<'PY'\nimport yaml,sys,json\nprint(json.dumps(yaml.safe_load(open(sys.argv[1],'r',encoding='utf-8')).get('assignees',[])))\nPY\n "$ISSUE_YAML")
  gh issue create --title "$TITLE" --body "$BODY" --label "$LABELS" --assignee "$ASSIGNEES"
fi
