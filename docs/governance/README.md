# Governance Standards

This directory records governance standards and the latest compliance enforcement patterns for the gh_COPILOT project.

## Core Principles
- **Transparency:** Record significant decisions and changes within the repository.
- **Compliance:** Follow licensing requirements and project policies.
- **Review:** Every change undergoes peer review through pull requests.

## Coding Standards
- Adhere to PEP 8 style guidelines with a 120-character line limit.
- Use `snake_case` for functions and variables and `CamelCase` for classes.
- Include type hints and docstrings for public functions.
- Run `ruff` and `pytest` before submitting a pull request.

## Compliance Enforcement Patterns
Automated compliance metrics gate changes by evaluating lint results, test outcomes, and placeholder audits. The safe pytest runner logs a summary and removes coverage flags when plugins are missing, preventing hangs. Dual-copilot validation and anti-recursion safeguards remain mandatory; a failing composite score blocks deployments and pull requests until issues are resolved.
