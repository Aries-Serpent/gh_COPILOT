
#!/usr/bin/env python3
import argparse, os, json, subprocess, sys, shutil, tempfile, time
from pathlib import Path

try:
    import yaml  # PyYAML
except ImportError:
    print("Installing PyYAML...", file=sys.stderr)
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyYAML"])
    import yaml

import urllib.request

API = "https://api.github.com"

def sh(cmd, cwd=None, check=True):
    print("+", " ".join(cmd))
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and res.returncode != 0:
        print(res.stdout)
        print(res.stderr, file=sys.stderr)
        raise SystemExit(res.returncode)
    return res

def gh_request(method, path, token, payload=None, accept="application/vnd.github+json"):
    url = f"{API}{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": accept,
        "User-Agent": "gh-copilot-wire/1.0"
    }
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        print(f"ERROR {method} {url}: {e.code} {e.reason}\n{err_body}", file=sys.stderr)
        raise

def ensure_milestone(owner, repo, token, milestone_name):
    if not milestone_name:
        return None
    # List milestones and find by title
    items = gh_request("GET", f"/repos/{owner}/{repo}/milestones?state=all", token)
    for m in items:
        if m.get("title") == milestone_name:
            return m["number"]
    # Create if not present
    created = gh_request("POST", f"/repos/{owner}/{repo}/milestones", token, {"title": milestone_name})
    return created["number"]

def create_issue(owner, repo, token, yml_path):
    data = yaml.safe_load(Path(yml_path).read_text(encoding="utf-8"))
    title = data.get("title") or "Enterprise compliance metrics integration & gaps closure"
    desc = data.get("description", "")
    labels = data.get("labels") or []
    assignees = data.get("assignees") or []
    milestone_name = data.get("milestone") or None

    ms_number = ensure_milestone(owner, repo, token, milestone_name)
    payload = {
        "title": title,
        "body": desc,
    }
    if labels: payload["labels"] = labels
    if assignees: payload["assignees"] = assignees
    if ms_number: payload["milestone"] = ms_number

    issue = gh_request("POST", f"/repos/{owner}/{repo}/issues", token, payload)
    print(f"Issue created: #{issue['number']} — {issue['html_url']}")
    return issue

def create_branch_push_and_pr(repo_full, token, branch, whitepaper, issue_yaml, pr_title, pr_body):
    owner, repo = repo_full.split("/", 1)
    tmp = Path(tempfile.mkdtemp(prefix="gh-copilot-wire-"))
    try:
        sh(["git", "clone", f"https://{owner}:{token}@github.com/{owner}/{repo}.git", str(tmp)], check=True)
        sh(["git", "checkout", "-b", branch], cwd=tmp, check=True)

        # Place files
        dest_wp = tmp / "documentation" / "generated"
        dest_wp.mkdir(parents=True, exist_ok=True)
        shutil.copy2(whitepaper, dest_wp / Path(whitepaper).name)

        dest_issue = tmp / ".github" / "ISSUE_TEMPLATE"
        dest_issue.mkdir(parents=True, exist_ok=True)
        shutil.copy2(issue_yaml, dest_issue / Path(issue_yaml).name)

        sh(["git", "add", "-A"], cwd=tmp)
        sh(["git", "commit", "-m", pr_title], cwd=tmp)
        sh(["git", "push", "--set-upstream", "origin", branch], cwd=tmp)

        # Open PR
        payload = {
            "title": pr_title,
            "head": branch,
            "base": "master",
            "body": pr_body
        }
        pr = gh_request("POST", f"/repos/{owner}/{repo}/pulls", token, payload)
        print(f"PR opened: #{pr['number']} — {pr['html_url']}")
        return pr
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def main():
    ap = argparse.ArgumentParser(description="Wire YAML issue + Whitepaper PR for gh_COPILOT")
    ap.add_argument("--repo", required=True, help="owner/repo, e.g., Aries-Serpent/gh_COPILOT")
    ap.add_argument("--branch", required=True, help="new branch name to create")
    ap.add_argument("--whitepaper", required=True, help="path to Markdown whitepaper")
    ap.add_argument("--issue-yaml", required=True, help="path to YAML issue file")
    ap.add_argument("--pr-title", required=True)
    ap.add_argument("--pr-body", required=True)
    ap.add_argument("--create-issue", action="store_true", help="create GitHub issue from YAML")
    args = ap.parse_args()

    token = os.environ.get("GH_TOKEN")
    if not token:
        print("ERROR: GH_TOKEN environment variable not set.", file=sys.stderr)
        sys.exit(2)

    owner, repo = args.repo.split("/", 1)

    if args.create_issue:
        create_issue(owner, repo, token, args.issue_yaml)

    create_branch_push_and_pr(args.repo, token, args.branch, args.whitepaper, args.issue_yaml, args.pr_title, args.pr_body)

if __name__ == "__main__":
    main()
