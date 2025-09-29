DRY_RUN Analysis: tools, ops, deploy, monitoring, mcp, analysis, agents
=======================================================================

tools/
- Numerous snapshot automation and codex-specific helpers (apply_* scripts, CI guards, vendor policies). We already ingested the minimal local tools we need (precommit_block_large, validate_fences, semgrep rules) and have clw/safe_rg.
- Recommendation: Do not ingest remaining tools/*.

ops/
- Threat model docs and operational guidance. Not runtime code; snapshot-specific.
- Recommendation: Not adopted.

deploy/
- Deployment code (Python/Helm charts). Out-of-scope for local-only automation per guardrails.
- Recommendation: Not adopted.

monitoring/
- Placeholder .gitkeep; broader monitoring handled in current repo via our own systems if needed. Snapshot tree not integrated.
- Recommendation: Not adopted.

mcp/
- MCP config/server scaffolding. Not used in current gh_COPILOT workflow; out-of-scope.
- Recommendation: Not adopted.

analysis/
- Snapshot analyses (audit_pipeline, metrics, providers). Not part of our automation core.
- Recommendation: Not adopted.

agents/
- Separate agent client package (own pyproject). Conflicts with repo structure and guardrails.
- Recommendation: Not adopted.

Decision
- Mark the above directories as PENDING deletion from the snapshot.

