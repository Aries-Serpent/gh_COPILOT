Sources:
- E:/gh_COPILOT/archive/copied_codex_codebase/conftest.py
- E:/gh_COPILOT/archive/copied_codex_codebase/README.md and docs

Targets:
- tests/ (we added minimal new tests)
- docs/automation_onboarding.md (new doc to write)

Summary:
- Snapshot conftest.py manipulates sys.path and sets env for GPUs; our project
  has broader tests and fixtures. For our minimal test set, we avoid global
  side effects.

Suggested integration:
- Add a brief onboarding doc explaining the new automation core, guardrails,
  dry-run/apply semantics, and demo script usage.

Apply action:
- Write docs/automation_onboarding.md.

