DRY_RUN Analysis: Snapshot Services
==================================

Path: archive/copied_codex_codebase/services

Subdirectories
- api: FastAPI service relying on codex_ml (torch, tokenizers, LoRA adapters). Heavy ML deps; out of scope.
- ita: Internal Tools API (FastAPI) with repo hygiene endpoints, API key storage, and openapi spec.

Applicability
- api: Not applicable; requires codex_ml and GPU/torch stacks. Conflicts with guardrails.
- ita: While lightweight FastAPI, it introduces a web service with API key store and repo operations beyond our automation scope. Our current integration focuses on local-only automation, not standing APIs.

Recommendation
- Do not ingest either service. Keep the codebase focused on local automation and tooling.

Decision
- Mark `services/` for PENDING deletion in the snapshot.

