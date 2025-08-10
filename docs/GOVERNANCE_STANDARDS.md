# Governance Standards

This document defines organizational rules and coding standards for the gh_COPILOT
project. All contributors must comply with these policies to maintain a secure and
collaborative codebase.

## Core Principles
- **Transparency:** Record significant decisions and changes within the repository.
- **Compliance:** Follow licensing requirements and project policies.
- **Review:** Every change undergoes peer review through pull requests.

## Coding Standards
- Adhere to PEP 8 style guidelines with a 120-character line limit.
- Use `snake_case` for functions and variables and `CamelCase` for classes.
- Include type hints and docstrings for public functions.
- Run `ruff` and `pytest` before submitting a pull request.

## Contributor Expectations
- Run `bash setup.sh`, activate the virtual environment, and execute `ruff` and `pytest` before committing.
- Reference these standards and the [Repository Guidelines](REPOSITORY_GUIDELINES.md) in proposals and pull requests.
- Respect the dual-copilot validation and database-first principles.

## Compliance Enforcement Patterns
Automated compliance metrics now gate changes by evaluating lint results, test outcomes, placeholder audits, and session wrap-ups. These patterns integrate with dual-copilot validation and anti-recursion safeguards to uphold governance standards. A failing composite score blocks deployments and pull requests until issues are resolved, providing transparent and auditable enforcement.

## Compliance Scoring Rules
Compliance scores combine four weighted components:

- **Lint Score (30%)** – percentage of files passing `ruff` checks.
- **Test Score (40%)** – percentage of automated tests passing.
- **Placeholder Score (20%)** – proportion of resolved TODO/FIXME placeholders.
- **Session Success Rate (10%)** – proportion of sessions that complete `start_session`/`end_session` without integrity violations.

The composite compliance score is calculated as:

```
composite = 0.3 * lint_score + 0.4 * test_score + 0.2 * placeholder_score + 0.1 * session_success_rate
```

A composite score below **85** blocks merges until issues are corrected.

## Placeholder Targets
- Maintain fewer than **5** open TODO/FIXME placeholders per **1,000** lines of code.
- Resolve at least **10** placeholders per week across active modules.
- Release branches must have **zero** unresolved placeholders before merge.

## ML Monitoring and Placeholder Audits
Machine-learning components must log performance and drift metrics to `analytics.db` via the unified monitoring interfaces. Placeholder audits run after each session and their results are stored in `placeholder_audit_snapshots` to satisfy enterprise governance requirements. Deviations from expected model behaviour or unresolved placeholders trigger compliance reviews and must be addressed before deployment.

## Session Lifecycle Requirements
- Invoke `start_session` at the beginning of every workflow and `end_session` upon completion.
- Persist session metadata, compliance scores, and audit results to `analytics.db` for traceability.
- Run zero-byte file checks and placeholder audits during `end_session` to confirm integrity.
- Mark sessions that fail integrity checks or leave placeholders unresolved as non‑compliant until corrected.
