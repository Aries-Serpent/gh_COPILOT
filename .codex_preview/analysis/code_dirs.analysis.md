DRY_RUN Analysis: Snapshot Code Directories
==========================================

Directories reviewed: codex_addons, codex_utils, codex_digest, codex_ml, training, torch, experiments, notebooks, nox_sessions

Findings
- codex_addons: ML-oriented extensions (e.g., metrics collectors). Tied to codex_ml and training stack.
- codex_utils: Logging/TensorBoard helpers (SummaryWriter), psutil/resource metrics; NDJSON logging class; checkpoint retention utils. These duplicate or exceed our minimal needs and add optional heavy deps.
- codex_digest: Error capture utilities and CLIs focused on snapshot tooling; we implemented minimal NDJSON logging already.
- codex_ml: Full ML package (CLI, data, models, PEFT hooks). Out of scope for gh_COPILOT automation core.
- training: Checkpoint managers, dataset loaders, cache logic; tightly coupled to codex_ml usage.
- torch: Namespace package placeholder indicating PyTorch-based integrations.
- experiments: Markdown experiments; documentation-like, not runtime code.
- notebooks: Jupyter notebooks; not part of production code.
- nox_sessions: Test sessions for utilities (e.g., fence tests); relies on nox.

Applicability
- The above directories introduce heavy ML dependencies or snapshot-specific runtime patterns. Integrating them would violate guardrails (no new deps) and is unrelated to our automation core objectives.

Recommendations
- Do not ingest these directories. Retain only our minimal `gh_copilot.automation` additions and auxiliary tools.

Decision
- Mark the listed directories as PENDING for deletion from the snapshot after confirmation.

