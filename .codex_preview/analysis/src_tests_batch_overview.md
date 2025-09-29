DRY_RUN Analysis: src, tests, and related code trees
====================================================

Paths: src, tests, tokenization, typer, copilot, db, data, artifacts, logs, temp, archive, .codex, .github, schemas

Findings
- src: Snapshot package code (codex/* training/cli). Not aligned with gh_COPILOT automation scope; would add large, unrelated code.
- tests: Snapshot test suite targets snapshot packages; not applicable.
- tokenization/typer: Snapshot subpackages/utilities; out of scope for our minimal integration.
- copilot/: extension artifacts (VS Code extension); unrelated to our repo structure.
- db/data/artifacts/logs/temp/archive: data, generated artifacts, temporary trees, and removed CI scripts — not part of the integration.
- .codex: snapshot-specific logs and analysis state; not needed.
- .github: snapshot GitHub docs/templates; we avoid remote CI activation and do not import these.
- schemas: snapshot JSON schemas for runs; not integrated into gh_COPILOT.

Decision
- Not adopted. Mark for deletion from the snapshot.

