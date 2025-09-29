Codex Snapshot Ingestion and Decommission Summary
=================================================

Scope
- Ingested minimal, local-only tooling (automation core, guardrails, exec/logging helpers,
  precommit fence validator, .codex large-file blocker, select semgrep rules).
- DRY_RUN-analyzed snapshot components; ingested only safe, relevant pieces; deleted non-adopted files/dirs.

Highlights
- Added `gh_copilot.automation` core and demo runner.
- Added `gh_copilot.compat.codex_snapshot_adapter` behind env flag.
- Added local configs (ruff/pytest/coverage) and docs.
- Ingested semgrep rules and pre-commit tools (stdlib-only).
- New: `scripts/har_ingest.py` phased HAR pipeline with DRY_RUN safety, guardrails, and NDJSON metrics.
- Removed snapshot directory after multi-batch DRY_RUN + APPLY.

Safety
- All commits include [skip ci]; no GitHub Actions were modified.
- No new networked dependencies were introduced.
