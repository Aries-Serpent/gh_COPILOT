# Communication Excellence Guide

This guide summarizes how to communicate changes effectively in the gh_COPILOT project.

## Commit Message Conventions
- Use **Conventional Commits** prefixes (`feat:`, `fix:`, `docs:`, `chore:`, etc.).
- Keep messages concise and explain the reason for the change.
- Run `ruff check .` and `pytest -q` before committing to ensure code quality.

## Recent Validation
The most recent linting run showed no issues using `ruff`. Automated tests
failed to complete due to environment limitations.

## Pull Request Template
1. **Summary** – brief description of the change.
2. **Testing** – mention linting and test results.
3. **Related Docs** – list updated or referenced documentation.
4. **Prompt Reference** – include the original request or issue link.

## Example Prompts
- "Add visual indicators to `maintenance_scheduler` progress bars."
- "Implement validation helper for database-first operations."
- "Revise README integration score and link to scheduler docs."
