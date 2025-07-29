# Proposed GitHub Issues

## 1. Replace Hardcoded Secret Keys with Env Variables
- **Labels**: security, bug
- **Assignee**: security-team
- **Description**: Several configuration files contain placeholder secrets. Ensure all secret values are loaded from environment variables and document the process in README.

## 2. Integrate OpenAI Codex into Workflow (API Key Handling)
- **Labels**: feature, devops
- **Assignee**: backend-team
- **Description**: Create a secure connector for OpenAI usage that reads the API key from `OPENAI_API_KEY` environment variable and logs usage metrics.

## 3. Complete Template Synchronizer Transaction Logic
- **Labels**: enhancement, database
- **Assignee**: database-team
- **Description**: `template_engine.template_synchronizer` lacks transaction management when updating template records. Implement SQLite transactions to ensure atomic updates.

## 4. Implement /dashboard/compliance in Flask UI
- **Labels**: feature, ui
- **Assignee**: web-team
- **Description**: The Flask dashboard does not expose the compliance overview endpoint. Add a route that serves the `placeholder_summary.json` file with progress metrics.

## 5. Implement Quantum Template Scoring Module
- **Labels**: research, quantum
- **Assignee**: research-team
- **Description**: The quantum scoring placeholders in `quantum_optimizer.py` should be replaced with functional scoring algorithms using the simulation utilities.

## 6. Consolidate Placeholder Audit Scripts and Fix Path Hardcoding
- **Labels**: refactor, tech debt
- **Assignee**: backend-team
- **Description**: `intelligent_code_analysis_placeholder_detection.py` duplicates logic from `code_placeholder_audit.py`. Consolidate these scripts and remove hardcoded paths.

## 7. Fix Dockerfile Entrypoint for Application Launch
- **Labels**: bug, devops
- **Assignee**: devops-team
- **Description**: Ensure the Dockerfile uses an explicit entrypoint script that sets required environment variables before starting `dashboard/enterprise_dashboard.py`.

## 8. Catalog missing and incomplete modules in gh_COPILOT
- **Labels**: documentation, analysis, help wanted, triage
- **Assignee**: maintainer
- **Description**: Collect and document all `STUB-*` references listed in `docs/DATABASE_FIRST_COPILOT_TASK_SUGGESTIONS.md`. Summarize the missing modules and features so maintainers can prioritize implementation work.
