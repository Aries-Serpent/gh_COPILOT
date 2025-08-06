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
