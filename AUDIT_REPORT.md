# Capability Audit Report

Generated: 2025-09-29
Branch: copilot_codex

| Capability | Domain | Owner | Status | DRY_RUN | Apply Guard | Prod Impact | Notes |
|---|---|---|---|---|---|---|---|
| Orchestration | Automation | <@owner> | Implemented | Yes | Yes | Medium | StepCtx validations + message log stream. |
| Guardrails | Safety | <@owner> | Implemented | Yes | Yes | High | Requires preview cleanup before APPLY; scans for backup recursion. |
| Exec | Runtime | <@owner> | Implemented | Yes | N/A | Medium | NO_NETWORK_EXEC env enforced; tests pending. |
| Logging | Observability | <@owner> | Implemented | Yes | N/A | Low | DRY_RUN redirects to .codex_preview before APPLY. |

Gaps & Next Actions
- Add focused unit tests for run_cmd and append_ndjson preview routing.
- Optimize guard_no_recursive_backups to allow explicit safe paths.
- Integrate messages output from run_phases into compliance metrics.

Rollback
- Use `git checkout -- gh_copilot/automation` to restore automation modules if regressions surface.
