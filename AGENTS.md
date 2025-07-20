# AGENTS Guide for ChatGPT Codex




# AI Agent Contribution Guidelines

*This `AGENTS.md` is intended for AI contributors (e.g., OpenAI Codex agents) working on this repository. It outlines the required environment setup, permitted actions, coding standards, testing procedures, and contribution conventions that the agent must follow to produce acceptable pull requests.*

## Environment Setup

Ensure the development environment is correctly configured before making changes:

* **Setup Script**: If a `setup.sh` script is present at the repository root, execute it (e.g. `bash setup.sh`) to perform initial setup (such as creating the virtual environment and installing required dependencies).
* **Virtual Environment**: Always activate the Python virtual environment before running commands. Use `source .venv/bin/activate` to activate the venv. This ensures you're using the project-specific packages.
* **Dependencies**: Do **not** attempt to install any new packages beyond what is specified in `pyproject.toml`. Only the listed dependencies are available for use. You cannot add new packages on your own. If an additional package is absolutely needed to complete a task, **do not** install it; instead, note this requirement in the pull request description for maintainers to review.

## Allowed Tools and Commands (Agent Behavior)

Follow these guidelines for executing commands and editing files:

* **Non-Interactive Commands Only**: Use only non-interactive shell commands to inspect and modify files. For example, use `cat` or `sed` to read or manipulate file contents, and use the `apply_patch` command to apply changes as unified diffs. **Do NOT** open interactive editors (no `vim`, `nano`, etc.) or any tool that requires user input.
* **Sandbox Restrictions**: The agent operates in an isolated environment. Do not start background services or make external network calls unless explicitly permitted. Focus on using the terminal tools available in the sandbox.
* **Playwright Browser**: If running end-to-end tests or any automation that requires a browser (e.g. using Playwright), use **Chromium only**. (Chromium is pre-installed; other browsers like Firefox or WebKit are not available.)
* **Single Source of Instructions**: There are no nested agent instruction files in this project. This `AGENTS.md` is the sole guide for AI agent behavior, so adhere to it and do not look for additional agent directives elsewhere.
* **Adhere to Instructions**: Follow the task prompt and these guidelines closely. Do not perform extraneous changes or stray from the requested task. The agent should work within the given scope and constraints at all times.

## Commit and PR Guidelines

To ensure contributions integrate smoothly, follow these conventions for commits and pull requests:

* **Conventional Commit Titles**: Format the commit and PR title using the Conventional Commits style (e.g., `feat: ...` for a new feature, `fix: ...` for a bug fix, etc.). In particular, use a concise prefix and description (for example, `fix: resolve issue with user login`).
* **Pull Request Description**: When writing the PR description, include the *original user prompt or issue* that led to this change (for context). Provide a brief summary of what was done to address it. If relevant, also mention any follow-up needed or any special notes (e.g., if a new dependency is required but not installed).
* **Scope of PR**: Each PR should ideally address a single focused issue or feature. Do not mix unrelated changes in one PR. Keep the changeset relevant to the prompt. If multiple steps are required to complete the task, group them into the same PR, but avoid creating separate PRs for one logical task.
* **Complete Solution**: Ensure that the changes fully solve the problem described in the prompt. The PR should not be a partial or work-in-progress solution. Before marking the task complete, verify that all requirements are met (and tests are passing, as noted below).
* **PR Content**: Aside from code changes, the PR should include any necessary updates to documentation or configuration. However, avoid gratuitous changes (no random formatting edits or refactors unrelated to the task). Every change should have a purpose tied to the prompt.

## Code Style and Linting

Maintain code quality by adhering to the project's style and running automated checks:

* **Follow Project Style**: Write code that is consistent with the existing codebase in format and conventions. Follow PEP8 guidelines for Python (which the linter will enforce) and use naming conventions and patterns similar to the existing code.
* **Linting and Formatting**: Use `ruff check` to lint the code for any errors or style issues, and use `ruff format` to automatically format the code. Address all issues flagged by the linter before committing. The code should pass **ruff** with no warnings.
* **Type Checking**: Run `pyright` to perform static type checking on the project. Ensure that your changes do not introduce type errors. Resolve any type-check issues reported.
* **Clean Code**: Remove any temporary debugging code or prints before finalizing changes. The final code should be clean and production-ready, with appropriate comments or docstrings where necessary to explain complex logic (follow the commenting style used in the repository).

## Testing and Validation

Verify that all tests pass and add new tests for new features or bug fixes:

* **Run Tests**: After making changes, always run the project's test suite to ensure nothing is broken. Use `pytest` to run tests (or the appropriate test command). For example:

  * Run backend/server tests with `pytest tests/test_server.py` if server logic was modified.
  * Run frontend/UI tests with `pytest tests/test_web.py` if frontend components were changed.
  * (If unsure, running `pytest` with no arguments will run all tests.)
* **Passing Tests**: Ensure that **all tests pass** before concluding the task. If any tests fail, debug and fix the issues. Do not ignore failing tests; they must be resolved or updated to reflect intentional changes in behavior.
* **Add Tests for New Code**: When you add new functionality or fix a bug, include corresponding tests:

  * For server-side features or fixes, add or update tests in `tests/test_server.py`.
  * For front-end features or UI changes, add or update tests in `tests/test_web.py`.
    Ensure new tests cover the relevant logic and edge cases, and that they also pass.
* **Iterate if Necessary**: If a test fails or a new test exposes an issue, revise the code to fix the problem and run the tests again. The agent should iterate until the test suite is green.
* **Automated Verification**: Rely on tests and linters as the gatekeepers for code quality. Do not consider the task done until both linting and all tests are successful.

## Project Structure and Conventions

Understand and follow the repository structure so that your changes integrate correctly:

* **Match Directory Structure**: Place new files or modules in their appropriate locations. For example, if implementing a backend feature, keep related code in the server/back-end directory or module (following the organization of existing server code). Similarly, front-end/UI changes should be made in the designated front-end portions of the project. Avoid creating new top-level directories; instead, use the existing structure.
* **Key Directories**: Familiarize yourself with important directories in the project:

  * `tests/` – contains test files (e.g., `test_server.py`, `test_web.py` as noted above).
  * *(Identify and use other relevant directories for source code – e.g., a backend or frontend directory – based on the current project structure.)*
* **Consistency**: Follow the naming conventions and file organization patterns already present. If similar functionality exists elsewhere in the codebase, use it as a reference for how to structure your solution.
* **No Duplicate Files**: Do not create duplicate or redundant files. If you need to extend functionality, modify existing files or add to existing modules unless a new file is absolutely necessary for a new component.
* **Documentation and Comments**: If your changes require it, update any relevant documentation or comments in the code to keep them up-to-date. Maintain clarity and helpfulness in comments for any complex sections of code.

By adhering to all of the above guidelines, the AI agent will produce changes that are easy for maintainers to review and integrate. **Always ensure that your contribution conforms to these rules before marking the task as complete.**

======

Understood. I will now analyze the `gh_COPILOT` repository to identify all environment variables—both required and optional—that should be set within the ChatGPT - Codex environment settings. I’ll provide variable keys, inferred default values, and a brief description of each for human context. I’ll return shortly with a structured list you can input directly into the Codex environment configuration.


# Environment Configuration for ChatGPT–Codex (gh\_COPILOT Toolkit)

Properly setting environment variables is crucial for running the **gh\_COPILOT** toolkit in the ChatGPT-Codex environment. Below are the **required** and **optional** environment variables to configure, along with recommended default values and their purposes.

## Required Environment Variables

* **GH\_COPILOT\_WORKSPACE** – **Absolute path to the repository workspace root**. This variable must point to the root directory of the `gh_COPILOT` project (e.g. `/path/to/workspace`). All tests and scripts use this path to locate databases and configuration files. If not set, the code will fall back to the current working directory by default. (In the provided Docker container, it defaults to `/app`, but you should explicitly set it to your workspace path.)

* **GH\_COPILOT\_BACKUP\_ROOT** – **Path to an external backup directory**, **outside** of the workspace. This is required to enforce anti-recursion rules (backups must not be stored under the workspace). If not set, the toolkit will default to a temp location (e.g. `E:/temp/gh_COPILOT_Backups` on Windows or `/tmp/<user>/gh_COPILOT_Backups` on Linux). It’s recommended to set this to a dedicated backup folder on your system.

## Optional (Additional) Environment Variables

* **WORKSPACE\_ROOT** – *Alias for* **GH\_COPILOT\_WORKSPACE**. In the example `.env` file it is set to the same path as `GH_COPILOT_WORKSPACE`. While the code primarily uses `GH_COPILOT_WORKSPACE`, you can set `WORKSPACE_ROOT` as well (to the same value) for consistency or if any legacy components reference it.

* **FLASK\_SECRET\_KEY** – **Secret key string for Flask web apps**. Used to secure sessions and cookies in the optional web dashboard/UI. By default the example `.env` uses a placeholder `'your_secret_key'` – you **should replace this** with a strong, random string for production (e.g. a 32-byte hex string). This is only needed if you run the Flask-based enterprise dashboard; it ensures features like session management or CSRF protection function correctly.

* **FLASK\_RUN\_PORT** – **Port number for the Flask development server** (if using the Flask CLI to run the app). The example default is **`5000`**. You can change this if you need the Flask web interface to listen on a different port in your environment. (Note: When running the dashboard via the provided script, it may use a hard-coded port like 8080, but this env var is used when launching via `flask run` or similar dev commands.)

* **CONFIG\_PATH** – **Path to a custom configuration file** (YAML or JSON). This is optional; if set, it should point to a config file (e.g. `/path/to/config.yml`) that some utilities or scripts will load for configuration settings. If not provided, the system uses the default configuration file (`enterprise.json`) located in the `config/` folder of the workspace. Use this if you need to override default configuration by pointing the toolkit to a specific config file.

* **WEB\_DASHBOARD\_ENABLED** – **Flag to enable the web dashboard logging**. Optional toggle (expects **`"1"` for true**). If set to `"1"`, performance metrics will be logged with a `[DASHBOARD]` tag for integration with the web dashboard interface. By default (unset or `"0"`), these dashboard metric logs are disabled. Set this to `"1"` only if you are actively using the real-time web dashboard feature for monitoring performance.

Each of the above variables helps ensure the Codex container and toolkit operate correctly. Setting **GH\_COPILOT\_WORKSPACE** and **GH\_COPILOT\_BACKUP\_ROOT** is mandatory for path resolution and backup compliance. The others can be configured as needed based on which features (Flask web UI, custom configs, dashboard metrics) you plan to use. Always double-check that no secret or credential is accidentally hard-coded when configuring these variables.

**Sources:**

* gh\_COPILOT Documentation – *Environment Configuration*
* gh\_COPILOT Example `.env` file
* Relevant code references in gh\_COPILOT (for defaults and usage)

======

# Purpose
This guide is written for **automated ChatGPT Codex agents ** operating within the ** gh_COPILOT Toolkit**. It summarizes environment setup, Codex agent roles, and mandatory protocols pulled from documentation, instructions, and Copilot notes.

---

# 1. Environment Setup

1. ** Python 3.8+** required.
2. Install core dependencies:
    ```bash
    pip install - r requirements.txt
    ```
3. Optional extras:
    ```bash
    pip install - r requirements-web.txt     # Web dashboard
    pip install - r requirements-ml.txt      # ML/AI features
    ```
4. Run tests with `make test`. This installs packages from `requirements-test.txt` such as `tqdm`, `numpy`, `qiskit >= 1.4, < 2.0`, `qiskit-aer`, and `qiskit-machine-learning`.
5. Set the workspace root via the `GH_COPILOT_WORKSPACE` environment variable.
6. Populate the `.env` file with `GH_COPILOT_WORKSPACE` and `GH_COPILOT_BACKUP_ROOT`, then `source .env` to load these variables before running tasks.

Consult[`docs/INSTRUCTION_INDEX.md`](docs/INSTRUCTION_INDEX.md) for all available instruction modules.

---

# 2. Agent Roles

# Codex Agents
| Agent | Core Function |
|------- | ---------------|
| **DualCopilotOrchestrator ** | Primary executor with secondary validator. |
| **UnifiedMonitoringOptimizationSystem ** | Continuous health monitoring. |
| **QuantumOptimizationEngine ** | Aspirational quantum optimization. |
| **UnifiedScriptGenerationSystem ** | Generates scripts from `production.db` patterns. |
| **UnifiedSessionManagementSystem ** | Zero-byte and anti-recursion checks. |
| **UnifiedDisasterRecoverySystem ** | Backup and restore operations. |
| **LegacyCleanupSystem ** | Workspace cleanup and archival. |
| **WebGUIIntegrationSystem ** | Dashboard endpoints and reporting. |
| **EnterpriseComplianceValidator ** | Security and compliance audits. |
| **CompleteConsolidationOrchestrator ** | Database consolidation orchestrator. |

---

# 3. Core Protocols

1. ** Database-First Operations ** – Query `production.db` and related databases before any filesystem or code changes. All database files must remain below ** 99.9 MB**.
2. ** Dual Copilot Pattern ** – Every critical workflow uses a primary executor and a secondary validator.
3. ** Visual Processing Indicators ** – Scripts must include progress bars, start time logging, timeouts, ETC calculation, and real-time status updates.
4. ** Anti‑Recursion & Backup Rules ** – Backups must never be stored inside the workspace. Use the external root `/temp/gh_COPILOT_Backups` and validate paths with `validate_enterprise_operation()`.
5. ** Session Integrity & Continuous Operation ** – Sessions begin and end with integrity validation and zero-byte checks. Continuous monitoring runs 24/7.
6. ** Response Chunking ** – Responses should stay under 2, 000 tokens(1, 500–1, 800 preferred) and start with anti-recursion validation.
7. ** Quantum & AI Protocols ** – Quantum features are aspirational until fully implemented and tested. Placeholders must not be treated as production code.

---

# 4. Coding & Contribution Standards

- Use type hints and docstrings.
- Follow PEP 8/flake8
format code with `autopep8` and `isort`.
- Do ** not ** modify version‑controlled SQLite databases.
- Add or update unit tests when modifying code and run `make test`.
- Keep commit messages short and imperative.
- Track documentation metrics with `scripts/generate_docs_metrics.py` and verify via `scripts/validate_docs_metrics.py`. Both scripts accept `--db-path` for specifying an alternate database.

---

# 5. Agent Lifecycle Management

- Register new agents in this file and deprecate obsolete ones.
- Log critical actions to audit databases for traceability.
- Support continuous improvement and prepare for future quantum integration.

---

# Summary

ChatGPT Codex agents must strictly follow the database‑first mandate, dual Copilot validation, anti‑recursion rules, and visual processing standards. Database file sizes must never exceed ** 99.9 MB**. Quantum optimization references remain aspirational until fully implemented. This guide provides the baseline for Codex automation within the gh_COPILOT Toolkit.
