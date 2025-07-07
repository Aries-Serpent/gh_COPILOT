
# AGENTS Guide

## Repository Overview
This project contains deployment, monitoring, and automation scripts. Some documents reference
"quantum optimization" or other advanced capabilities. These features are **not** implemented and
should be treated as future plans only.

## Environment Setup
- Python **3.8+** is required (see `pyproject.toml`).
- Install dependencies with `pip install -r requirements.txt`.
- Optional extras:
  - `pip install -r requirements-web.txt` – web dashboard
  - `pip install -r requirements-ml.txt` – machine learning features
- Run tests with `make test`. This installs `requirements-test.txt` and executes `pytest`.
- The default workspace root is `/path/to/workspace` (override with `GH_COPILOT_WORKSPACE`).
  Example overrides:
    - Windows: `set GH_COPILOT_WORKSPACE=C:\Users\YourName\workspace`
    - Linux/macOS: `export GH_COPILOT_WORKSPACE=/home/yourname/workspace`

## Working Directories
- Canonical scripts live in `scripts/`; files under `scripts/deployment/` are legacy references.
- SQLite databases reside in `databases/` and are used by multiple modules.
- Logs are stored in `logs/` and reports are written to `reports/`.

## Development Workflow
1. Fork the repository and create a feature branch.
2. Make changes – update scripts in `scripts/` when modifying deployment logic.
3. Add or update tests in `tests/` and run `make test` locally.
4. Submit a pull request summarizing the changes and update documentation (e.g., README files).

## Coding Conventions
- Follow PEP 8/flake8 style and include docstrings.
- Use type hints and the existing structured logging configuration.
- Include anti‑recursion checks in scripts to prevent nested workspace copies.
- Keep documentation up to date and organize nonessential files into subfolders (`scripts`, `tools`,
  `docs`, `tests`).
- When modifying scripts, create or update tests accordingly.

## Session Protocols
- Start each session with `COMPREHENSIVE_WORKSPACE_MANAGER.ps1 -SessionStart`, then run
  `python emergency_c_temp_violation_prevention.py --emergency-cleanup` and validation scripts.
- End sessions with `COMPREHENSIVE_WORKSPACE_MANAGER.ps1 -SessionEnd` and perform a final
  anti‑recursion check.
- Scan for zero-byte files at session start, before/after edits, and at shutdown. Backups should be
  stored **outside** the workspace (e.g., `E:/temp/gh_COPILOT_Backups`).
- Always validate file operations with `validate_enterprise_operation()` to enforce the workspace
  root, forbid argument-derived folder names, and reject recursive backup structures.

## Autonomous File Management
- Organization and classification routines must query `production.db` and follow its patterns.
- The project uses a **Primary Executor** and **Secondary Validator** model. The validator checks
  anti-recursion compliance, workspace root usage, and `C:\Temp` violations before approving work.

## Response Chunking (for Copilot interactions)
Responses should be broken into logical chunks under 2,000 tokens (preferably 1,500–1,800) and
begin with an anti‑recursion validation check.

## Caution
Quantum optimization and other advanced AI claims are aspirational. Do not present them as working
features unless corresponding code exists. Keep README files in sync with script updates and treat
any quantum-related sections as informational only.

---
This guide summarizes repository policies and should be consulted before making changes.

# Contributor Guidelines

This repository follows a few common conventions to help keep development consistent.

## Development Requirements
- **Python**: version 3.8 or higher is required.
- Install core dependencies with `pip install -r requirements.txt`.
- Optional extras are available in the `requirements-*.txt` files and may be installed as needed.

## Running Tests
- Tests rely on the `GH_COPILOT_WORKSPACE` environment variable. Set it to your workspace path if it is not already defined.
- Run tests with `make test`. You can also execute `pytest` directly once dependencies are installed.

## Formatting and Linting
- Format code with `autopep8` and sort imports with `isort`.
- Lint the project using `flake8`.

## Commit Messages
- Use short, imperative commit messages (e.g., "Add support for new API") to keep history clear.

## Project Notes
- Keep documentation up to date with these limitations so users do not expect unsupported functionality.
- References to quantum optimization or other advanced capabilities in the documentation describe future goals. These features are **not implemented**.
- Do **not** modify any bundled SQLite databases under version control (see the `databases/` folder).
- Additional guidelines and DUAL COPILOT compliance requirements can be found in the `documentation/` directory.


