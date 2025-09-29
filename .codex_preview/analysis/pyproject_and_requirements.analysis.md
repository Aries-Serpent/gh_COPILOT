DRY_RUN Analysis: pyproject.toml and requirements
=================================================

Observation
- Snapshot `pyproject.toml` defines a separate installable project with optional heavy ML extras and console scripts. Requirements files include dev locks.

Applicability
- Our guardrails prohibit installing new dependencies beyond project-specified constraints. Incorporating a separate package configuration would conflict with the repo’s current structure and goals.

Recommendation
- Do not ingest snapshot `pyproject.toml`, `requirements*.txt`, or lock files. Keep our local-only tooling as configured.

Decision
- Not applicable here. Add to deletion post-plan after we finish all higher-priority integrations.

