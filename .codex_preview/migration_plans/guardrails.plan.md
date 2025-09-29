Sources:
- E:/gh_COPILOT/archive/copied_codex_codebase/.codex/guardrails.md

Targets:
- gh_copilot/automation/guardrails.py (implemented)

Summary:
- The snapshot emphasizes "DO NOT ACTIVATE ANY GitHub Actions" and local-only
  operation. Our guardrails enforce:
  - Block .github/workflows edits in APPLY mode
  - Prevent recursive backups
  - Forbid writing to C:/temp and E:/temp

Suggested integration:
- Keep guardrails as implemented. Optionally add docstrings referencing
  enterprise guard constraints and extend validate_no_forbidden_paths with a
  configurable denylist via env if needed later.

Apply action:
- No further code changes required now.

