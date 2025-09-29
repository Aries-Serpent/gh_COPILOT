DRY_RUN Analysis: Config and Framework Dirs
===========================================

Paths: configs, conf, hydra, omegaconf, yaml, requirements

Findings
- configs/conf: Hydra-style configuration trees (YAML + base_config.py). Out of scope for minimal automation core; we already added concise root configs (ruff/pytest/coverage).
- hydra/omegaconf/yaml: snapshot-vendored modules/placeholders; not part of our codebase. Introducing them would conflate concerns.
- requirements (dir) and top-level requirement files/locks: heavy ML stacks and pinned sets prohibited by guardrails.

Decision
- Not adopted. Mark these directories (and requirement files) for deletion from the snapshot.

