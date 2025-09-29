Codex Snapshot Ingestion Plan (DRY RUN)
=======================================

Snapshot root: `E:/gh_COPILOT/archive/copied_codex_codebase`

Status: Planning only (no APPLY). This plan enumerates priority files and the
intended migration targets with minimal diffs or creation suggestions.

Priority mappings
- codex_workflow.py → Fold orchestration patterns into `gh_copilot/automation/core.py`
  - Suggestion: Extend module docstring with a short example of StepCtx usage and
    sequencing notes inspired by snapshot.
- codex_task_sequence.py → Extract sequencing to `gh_copilot/automation/sequencer.py` (optional)
  - Suggestion: New module providing a thin wrapper to compose StepCtx with simple
    dependency annotations. DRY_RUN: Defer until core stabilizes.
- .codex/guardrails.md → Merge patterns into `gh_copilot/automation/guardrails.py`
  - Suggestion: Add explicit guards for workflow edits, backup recursion, and forbidden paths.
- .codex/ruff.json, lint-policy.json, GATES_REPORT.txt → Merge into `ruff.toml` and `.codex/`
  - Suggestion: Keep line-length=100, exclude archive and preview paths, store gates report under `.codex/`.
- conftest.py, pytest.ini → Merge useful markers into root `pytest.ini`
  - Suggestion: Adopt `-q` addopts and consolidate testpaths=tests.
- .pre-commit-config.yaml, .bandit.yml, .secrets.baseline → Update root config (local-only hooks)
  - Suggestion: Use `repo: local` hooks for ruff, end-of-file-fixer, trailing-whitespace, bandit, detect-secrets.
- README/docs patterns → Create `docs/automation_onboarding.md` describing automation core & guardrails.

Planned diffs (illustrative)
```diff
--- a/gh_copilot/automation/core.py
+++ b/gh_copilot/automation/core.py
@@
 """Core orchestration primitives ...
+
+# Example (from Codex snapshot patterns):
+# phases = [StepCtx(name="Analyze", desc="...", fn=analyze), ...]
+# run_phases(phases, dry_run=True)
 """
```

```diff
--- /dev/null
+++ b/gh_copilot/automation/sequencer.py
@@
+"""(Optional) Simple task sequencer for StepCtx collections."""
```

Apply criteria
- Only proceed when APPLY=1 and local checks pass (ruff/pytest if installed).
- After each successful apply, remove the source file from the snapshot and append an NDJSON log entry.
- If any check fails, revert and break down into smaller patches; record details in `docs/codex_integration_leftovers.md`.

DRY_RUN analysis (batch 2)
- codex_patch_runner.py / codex_update_runner.py / codex_setup.py / codex_script.py:
  - Not applicable; responsibilities overlap with gh_copilot.automation and introduce non-local tooling.
  - Added to deletion post-plan (pending apply).
- conftest.py:
  - Not applicable; interferes with repo test fixtures.
  - Added to deletion post-plan (pending apply).
- mkdocs.yml and mkdocs site:
  - Not adopted; we maintain focused docs in `docs/`.
  - Added to deletion post-plan (pending apply).
- pyproject.toml / requirements* / locks:
  - Not adopted; would conflict with repo structure and guardrails.
  - Added to deletion post-plan (pending apply).

Batch 2 APPLY deletions (post-DRY_RUN)
- codex_patch_runner.py / codex_update_runner.py / codex_setup.py / codex_script.py: not applicable; removed from snapshot.
- conftest.py: not applicable; removed from snapshot.
- mkdocs.yml: docs site not adopted; removed from snapshot.
- pyproject.toml: separate package config not adopted; removed from snapshot.
- tools/ci_guard.py: overlaps with guardrails; removed from snapshot.
- tools/pip_audit_wrapper.py: out of scope; removed from snapshot.
- tools/label_policy.json / tools/label_policy_lint.py: snapshot-specific; removed from snapshot.

Status updates (APPLY)
- codex_workflow.py: patterns folded into core docs; source removed from snapshot.
- .codex/ruff.json: merged into `ruff.toml`; source removed from snapshot.
- pytest.ini (snapshot): replaced by root pytest.ini; source removed from snapshot.
- .pre-commit-config.yaml (snapshot): replaced by local-only hooks; source removed from snapshot.
- GATES_REPORT.txt (snapshot root): merged into `.codex/GATES_REPORT.txt`; source removed from snapshot.
- .codex/guardrails.md: concepts integrated into guardrails module; source removed from snapshot.
- .pre-commit-hybrid.yaml / .pre-commit-ruff.yaml: superseded by root pre-commit; sources removed from snapshot.
- .coveragerc (snapshot): replaced by root coverage config; source removed from snapshot.
- .secrets.baseline (snapshot): intentionally not adopted; removed from snapshot.
- .bandit.yml / bandit.yaml (snapshot): policy deferred; removed from snapshot for now.
- docker-compose.yml / Dockerfile / Dockerfile.gpu (snapshot): not adopted; removed from snapshot.
- Makefile / codex.mk (snapshot): not adopted; removed from snapshot.
- noxfile.py / tox.ini / .dockerignore (snapshot): not adopted; removed from snapshot.
- semgrep_rules/default.yml and semgrep_rules/python-basic.yml: ingested into repo for optional local scanning; removed from snapshot.
- tools/safe_rg.sh: already present in repo; snapshot copy removed after DRY_RUN confirmation.
- tools/precommit_block_large.py and tools/validate_fences.py: ingested into repo tools; removed from snapshot after DRY_RUN analysis.
- Batch 4 APPLY code directory deletions (post-DRY_RUN)
- Removed snapshot code directories: codex_addons, codex_utils, codex_digest, codex_ml,
  training, torch, experiments, notebooks, nox_sessions
- Batch 3 APPLY docs deletions (post-DRY_RUN)
- Snapshot root docs removed: README.md, CHANGELOG.md, CHANGELOG_CODEX.md,
  CHANGELOG_SESSION_LOGGING.md, CODEBASE_AUDIT_2025-08-26_203612.md,
  Codex_Questions.md, DEFERRED.md, ERROR_LOG.md, OPEN_QUESTIONS.md,
  _codex_codex-ready-sequence-and-patches-2025-09-27.md,
  _codex_status_update-0C_base_-2025-09-27.md
- Snapshot doc directories removed: docs/, documentation/, reports/, examples/
