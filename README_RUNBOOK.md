
# gh_COPILOT — Issue & PR Wiring Kit

This kit lets you **(1) create a GitHub Issue** from your YAML and **(2) open a PR** that adds:
- the Markdown white‑paper under `documentation/generated/`
- the YAML issue under `.github/ISSUE_TEMPLATE/`

## Prereqs
- Python 3.10+
- `git` installed
- A GitHub **personal access token** with `repo` scope in env: `GH_TOKEN`
- Network access to `github.com`

## Quickstart

### A) One‑shot Python runner
```bash
export GH_TOKEN=YOUR_TOKEN
python wire_issue_and_pr.py   --repo Aries-Serpent/gh_COPILOT   --branch feature/whitepaper-issue-2025-08-08   --whitepaper "./gh_COPILOT_Project_Whitepaper_Blueprint_2025-08-08.md"   --issue-yaml "./Issue_2025-08-08.yaml"   --pr-title "docs: add whitepaper & issue template"   --pr-body "Adds whitepaper to documentation/generated and stores YAML issue in .github/ISSUE_TEMPLATE/."   --create-issue
```

### B) gh CLI option (if you prefer CLI)
```bash
export GH_TOKEN=YOUR_TOKEN
bash gh_cli_wire_issue_and_pr.sh   Aries-Serpent/gh_COPILOT   feature/whitepaper-issue-2025-08-08   ./gh_COPILOT_Project_Whitepaper_Blueprint_2025-08-08.md   ./Issue_2025-08-08.yaml   "docs: add whitepaper & issue template"   "Adds whitepaper to documentation/generated and stores YAML issue in .github/ISSUE_TEMPLATE/."   --create-issue
```

## Notes
- The Python script parses the provided YAML to extract `title`, `labels`, `assignees`, `milestone` and the long Markdown body under `description:` when creating the issue.
- Projects linking is optional and may require GraphQL; this kit omits that for reliability.
- If the milestone doesn’t exist, the script will create it.
- If you don’t want to open the Issue, omit `--create-issue`.
