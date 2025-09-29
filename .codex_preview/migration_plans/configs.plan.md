Sources:
- E:/gh_COPILOT/archive/copied_codex_codebase/pytest.ini
- E:/gh_COPILOT/archive/copied_codex_codebase/.pre-commit-config.yaml
- E:/gh_COPILOT/archive/copied_codex_codebase/.bandit.yml
- E:/gh_COPILOT/archive/copied_codex_codebase/.codex/ruff.json
- E:/gh_COPILOT/archive/copied_codex_codebase/GATES_REPORT.txt

Targets:
- pytest.ini (added)
- .pre-commit-config.yaml (local-only hooks added)
- ruff.toml (added)
- .codex/GATES_REPORT.txt (added)

Summary:
- We added minimal configs that are local-only and avoid networked hooks.
- Snapshot configs include remote repos and heavy hooks; we intentionally avoid
  those here per guardrails. Bandit policy could be carried over later.

Suggested integration:
- Consider porting selected markers from snapshot pytest.ini into root pytest.ini.
- Optionally add .bandit.yml if local bandit runs are desired; keep it minimal.

Apply action:
- Our current configs satisfy scope. Defer further merges unless needed.

