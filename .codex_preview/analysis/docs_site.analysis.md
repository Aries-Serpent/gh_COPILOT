DRY_RUN Analysis: mkdocs.yml and documentation site
===================================================

Observation
- Snapshot includes `mkdocs.yml` and extensive documentation trees. Our current integration added targeted onboarding docs and migration plans, but we are not adopting a full mkdocs site.

Applicability
- Migrating an entire docs site adds maintenance burden beyond the scope of the automation-focused integration.

Recommendation
- Do not ingest `mkdocs.yml` or the mkdocs-specific structure. Continue to keep docs minimal within `docs/`.

Decision
- Not applicable presently. Add `mkdocs.yml` and mkdocs-only site structure to deletion post-plan.

