DRY_RUN Analysis: tools (clw, safe_rg)
=====================================

Snapshot vs repo
- Snapshot tools list is extensive. Key items under consideration:
  - tools/safe_rg.sh — present in snapshot; repo already has `tools/safe_rg.sh`.
  - tools/clw.py — not present in snapshot; repo already has `tools/clw.py`.

Applicability
- Both wrappers are relevant to local-only workflows and output safety. Since
  the repo already contains them, no ingestion is required.

Decision
- Mark snapshot `tools/safe_rg.sh` for deletion post-plan (already present in repo).

