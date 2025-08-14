## 1) Quick‑Start: Branch Creation & PR Commands

> Replace `origin` with your remote name if different; replace `MarcJ` with your user if you prefer.

```bash
# Ensure you are up to date
git checkout main
git pull --ff-only

# G1: SSOT Reconciler
git checkout -b feat/ssot-reconciler
# Add the reconciler, schema, tests (per Codex tasks); stage workflow in .github/workflows/status-reconciler.yml
git add scripts/docs_status_reconciler.py \
        scripts/schemas/status_index.schema.json \
        tests/docs_status_reconciler_test.py \
        .github/workflows/status-reconciler.yml \
        docs/PHASE5_TASKS_STARTED.md

git commit -m "feat(ssot): add reconciler, schema, tests, and CI drift check"
git push -u origin feat/ssot-reconciler

# (Optional) Open PR with gh CLI
# gh pr create --title "SSOT Reconciler & Drift CI" --body "Adds reconciler and CI gate for status drift."

# G2: Dashboard Compliance UI
git checkout main && git pull --ff-only
git checkout -b feat/dashboard-compliance
# Add or edit Flask views/templates/static; stage workflow in .github/workflows/dashboard-compliance.yml
git add web_gui/scripts/flask_apps/enterprise_dashboard.py \
        templates/compliance/ \
        templates/partials/ \
        static/js/compliance.js \
        static/js/exports.js \
        static/css/compliance.css \
        .github/workflows/dashboard-compliance.yml

git commit -m "feat(dashboard): compliance views, exports, deep links, version stamp, CI"
git push -u origin feat/dashboard-compliance
# gh pr create --title "Dashboard: Compliance Section" --body "Adds Compliance nav, drill-downs, exports, deep links."

# G3: Governance Gate
git checkout main && git pull --ff-only
git checkout -b feat/governance-gate
# Add policy tests + runner + CI; optional attestation helper
git add policy_tests/ \
        scripts/policy/run_policy_checks.py \
        scripts/policy/generate_attestation.py \
        .github/workflows/governance-gate.yml \
        compliance/attestations/README.md

git commit -m "feat(governance): policy-as-code tests, runner, CI gate, attestations"
git push -u origin feat/governance-gate
# gh pr create --title "Governance Gate (Policy-as-Code)" --body "Adds tests, runner, and CI gate with waiver support."
```

---

## 2) Workflow YAMLs (drop‑in)

Each YAML is **ready to place** under `.github/workflows/`. Names are unique to avoid job collisions; paths filters minimize unrelated triggers.

### 2.1 `.github/workflows/status-reconciler.yml`

```yaml
name: Status Reconciler

on:
  push:
    branches: [ main ]
    paths:
      - 'docs/PHASE5_TASKS_STARTED.md'
      - 'scripts/docs_status_reconciler.py'
      - 'scripts/schemas/status_index.schema.json'
      - '.github/workflows/status-reconciler.yml'
  pull_request:
    paths:
      - 'docs/PHASE5_TASKS_STARTED.md'
      - 'docs/task_stubs.md'
      - 'scripts/docs_status_reconciler.py'
      - 'scripts/schemas/status_index.schema.json'
      - '.github/workflows/status-reconciler.yml'

permissions:
  contents: read
  actions: read
  checks: write
  pull-requests: write

jobs:
  drift-check:
    name: SSOT Drift Check
    runs-on: ubuntu-latest
    steps:
        - name: Checkout
          uses: actions/checkout@v4
          with:
            lfs: true
            fetch-depth: 0

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements-test.txt', 'requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Install deps
        run: |
          if [ -f requirements-test.txt ]; then pip install -r requirements-test.txt; fi
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

      - name: Validate SSOT & generate artifacts (check-only)
        run: |
          python scripts/docs_status_reconciler.py --check
        continue-on-error: true
        id: check

      - name: Upload diff on drift
        if: steps.check.outcome == 'failure'
        uses: actions/upload-artifact@v4
        with:
          name: ssot-drift-context
          path: |
            docs/task_stubs.md
            status_index.json

      - name: Fail on drift
        if: steps.check.outcome == 'failure'
        run: |
          echo "SSOT drift detected. See artifact ssot-drift-context." >&2
          exit 1
```

---

### 2.2 `.github/workflows/dashboard-compliance.yml`

```yaml
name: Dashboard Compliance UI

on:
  pull_request:
    paths:
      - 'web_gui/**'
      - 'templates/**'
      - 'static/**'
      - '.github/workflows/dashboard-compliance.yml'
  push:
    branches: [ main ]
    paths:
      - 'web_gui/**'
      - 'templates/**'
      - 'static/**'

permissions:
  contents: read

jobs:
  build-and-smoke:
    name: Build & UI Smoke
    runs-on: ubuntu-latest
      steps:
        - name: Checkout
          uses: actions/checkout@v4
          with:
            lfs: true
            fetch-depth: 0

        - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements-web.txt', 'requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Install web deps
        run: |
          if [ -f requirements-web.txt ]; then pip install -r requirements-web.txt; fi
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

      - name: Lint (ruff) — non-blocking
        run: |
          if command -v ruff >/dev/null 2>&1; then ruff check . || true; fi

      - name: Export version stamp
        run: echo "DASHBOARD_VERSION=$(git rev-parse --short HEAD)" >> $GITHUB_ENV

      - name: Smoke test endpoints (Python inline)
        run: |
          python - <<'PY'
          import os, sys, json
          from importlib import import_module
          # Basic import check for Flask dashboard module; adjust if app factory exists
          try:
              import_module('web_gui.scripts.flask_apps.enterprise_dashboard')
              print(json.dumps({"status":"import_ok"}))
          except Exception as e:
              print(json.dumps({"status":"import_failed","error":str(e)}))
              sys.exit(1)
          PY

      - name: Archive static artifacts (if present)
        if: ${{ always() }}
        uses: actions/upload-artifact@v4
        with:
          name: dashboard-static-preview
          path: |
            static/**
            templates/**
          if-no-files-found: ignore
```

---

### 2.3 `.github/workflows/governance-gate.yml`

```yaml
name: Governance Gate

on:
  pull_request:
    paths:
      - 'policy_tests/**'
      - 'scripts/policy/**'
      - 'compliance/attestations/**'
      - '.github/workflows/governance-gate.yml'

permissions:
  contents: read
  pull-requests: write

  jobs:
    policy-checks:
      name: Policy Tests & Gate
      runs-on: ubuntu-latest
      steps:
        - name: Checkout
          uses: actions/checkout@v4
          with:
            lfs: true
            fetch-depth: 0

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements-test.txt', 'requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Install deps
        run: |
          if [ -f requirements-test.txt ]; then pip install -r requirements-test.txt; fi
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

      - name: Run policy tests (pytest)
        run: |
          if [ -d policy_tests ]; then pytest -q policy_tests/; else echo "no policy_tests dir"; fi

      - name: Summarize to analytics (optional)
        run: |
          if [ -f scripts/policy/run_policy_checks.py ]; then python scripts/policy/run_policy_checks.py; fi

      - name: Check waiver (optional)
        id: waiver
        shell: bash
        env:
          PR_NUMBER: ${{ github.event.pull_request.number }}
        run: |
          FILE=.governance-waivers/${PR_NUMBER}.yml
          if [ -f "$FILE" ]; then
            echo "waiver=true" >> $GITHUB_OUTPUT
          else
            echo "waiver=false" >> $GITHUB_OUTPUT
          fi

      - name: Block on failures without waiver
        if: failure() && steps.waiver.outputs.waiver != 'true'
        run: |
          echo "Governance checks failed and no valid waiver found." >&2
          exit 1

      - name: Comment summary (best effort)
        if: always()
        uses: marocchino/sticky-pull-request-comment@v2
        with:
          header: governance-gate
          message: |
            **Governance Gate** completed.
            - Status: ${{ job.status }}
            - Waiver: ${{ steps.waiver.outputs.waiver }}
```

---

## 3) Notes on Concurrency & Isolation

* **Distinct workflow names** avoid Actions UI collisions.
* **Paths filters** constrain triggers to relevant surfaces.
* **No schema change** in `dashboard-compliance.yml` keeps it read‑only.
* **Governance Gate** runs on PR only, with optional waivers.
* **Status Reconciler** runs on both PR and `main` pushes touching SSOT surfaces; fails fast on drift.

## 4) Next Steps (Optional Generators)

* Add a small Codex prompt to auto‑create the three YAMLs when a branch is generated.
* Produce a `.devcontainer/` with Python 3.11 and SQLite tools to standardize local CI‑like runs.

---

### Appendix: Minimal Make Targets (optional)

```Makefile
.PHONY: check-ssot
check-ssot:
	python scripts/docs_status_reconciler.py --check

.PHONY: policy
policy:
	pytest -q policy_tests/
	python scripts/policy/run_policy_checks.py || true

.PHONY: dashboard-dev
dashboard-dev:
	export DASHBOARD_VERSION=$$(git rev-parse --short HEAD); \
	python web_gui_integration_system.py
```
