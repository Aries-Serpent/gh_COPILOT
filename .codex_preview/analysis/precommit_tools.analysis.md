DRY_RUN Analysis: pre-commit helper tools
=========================================

Reviewed snapshot tools:
- tools/precommit_block_large.py — stdlib-only; enforces .codex file size ceiling. Useful and safe.
- tools/validate_fences.py — stdlib-only; validates Markdown code fences; optional local check.
- tools/ci_guard.py — overlaps with guardrails; not needed.
- tools/pip_audit_wrapper.py — pulls audit behavior; out of scope given guardrails.
- tools/label_policy.json / label_policy_lint.py — snapshot-specific workflows; not adopted here.

Decisions
- Ingest: precommit_block_large.py, validate_fences.py
- Not adopted (PENDING delete): ci_guard.py, pip_audit_wrapper.py, label_policy.json, label_policy_lint.py

