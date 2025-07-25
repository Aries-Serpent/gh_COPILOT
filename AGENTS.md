# AGENTS Guide for ChatGPT Codex

*This guide is intended for AI contributors (OpenAI Codex/ChatGPT agents) working on the **gh\_COPILOT** repository. It outlines the required environment setup, permitted actions, coding standards, testing procedures, and other protocols that the agent **must** follow to produce acceptable pull requests.*
Additional instruction modules reside in `.github/instructions/`. These `.instructions.md` files provide focused guidance on specialized workflows and supplement this main guide. Key compliance topics include **DUAL_COPILOT_PATTERN**, **ZERO_TOLERANCE_VISUAL_PROCESSING**, **COMPREHENSIVE_SESSION_INTEGRITY**, **AUTONOMOUS_FILE_MANAGEMENT**, **RESPONSE_CHUNKING**, **WEB_GUI_INTEGRATION**, **QUANTUM_OPTIMIZATION**, **PHASE4_PHASE5_INTEGRATION**, **SESSION_TEMPLATES**, **SESSION_INSTRUCTION**, **ENHANCED_LEARNING_COPILOT**, and **ENHANCED_COGNITIVE_PROCESSING**. Review these modules regularly to ensure your contributions remain in full compliance.


## Environment Setup

Ensure the development environment is correctly configured **before** making any changes or running code:

* **Setup Script**: If a `setup.sh` script is present at the repository root, run it (e.g. `bash setup.sh`) to perform initial setup tasks (creating the virtual environment, installing dependencies, etc.). This project provides a `setup.sh` – use it to avoid missing any required steps.
* **Verify `clw` Utility**: After setup, confirm `/usr/local/bin/clw` exists and is executable. If missing, copy `tools/clw.py` to `/usr/local/bin/clw` and make it executable. Run `clw --help` to verify it works.
* **Hard Output Limit**: The Codex terminal enforces a **1600-byte** maximum per line. Always pipe potentially long output through `clw` (e.g., `command | clw`) or redirect to a log file and read it in chunks. Adjust the limit with `CLW_MAX_LINE_LENGTH` if needed.
* **Python & Tools**: Use **Python 3.8+** (already provided in Codex). The setup will install necessary system packages (development headers, build tools, SQLite, etc.) and Python packages as specified by the project. Do **not** install additional packages beyond those listed in `requirements.txt` (and optional `requirements-web.txt`, `requirements-ml.txt`, etc.). **Only use** the dependencies declared by the project. If you believe a new package is required, **do not install it yourself** – instead, mention the need in the PR description for maintainers.
* **Virtual Environment**: Always activate the Python virtual environment after running setup. For example, use `source .venv/bin/activate` to ensure you’re using the project’s isolated environment and packages.
* **Environment Variables**: Certain environment variables must be set for the toolkit to function correctly. In particular:

  * **GH\_COPILOT\_WORKSPACE** – Absolute path to the repository’s root workspace. This should point to the project root (in the Codex container it defaults to `/app`, but set it explicitly). Many scripts use this to locate files and databases.
  * **GH\_COPILOT\_BACKUP\_ROOT** – Path to an **external** backup directory (must be outside the workspace). This enforces anti-recursion: backups **must not** be stored under the project root. If not set, the toolkit defaults to a temp directory (e.g. `/tmp/<user>/gh_COPILOT_Backups` on Linux). It’s recommended to set this to a dedicated folder.
  * *Optional variables:* **WORKSPACE\_ROOT** (alias for `GH_COPILOT_WORKSPACE`), **FLASK\_SECRET\_KEY** (for the optional Flask web UI, default `'your_secret_key'` – replace in production), **FLASK\_RUN\_PORT** (Flask dev server port, default 5000), **CONFIG\_PATH** (path to a custom config file if not using the default `config/enterprise.json`), **WEB\_DASHBOARD\_ENABLED** (`"1"` or `"0"` to toggle logging of performance metrics with `[DASHBOARD]` tags). Configure these as needed if using those features.
* After installing dependencies and setting variables, **run the test suite** (see [Testing and Validation](#testing-and-validation)) to verify the environment is correctly set up.

## Allowed Tools and Commands (Agent Behavior)

When using the terminal or editing files, the agent must adhere to the following rules:

* **Non-Interactive Commands Only**: Use only non-interactive shell commands for inspecting and modifying files. For example, use `cat`, `grep`, `sed`, or `jq` for reading or searching file contents, and use the `apply_patch` tool (provided by the Codex environment) to apply changes via unified diff. **Do NOT** open interactive editors (no `vim`, `nano`, etc.) or run any command that requires human input.
* **No External Network Calls**: The agent runs in a sandboxed environment with no internet access (except perhaps to fetch specified resources in setup). Do not attempt to download assets or call external APIs unless explicitly allowed by the task. Focus on local repository files and the tools available in the container.
* **Sandbox Restrictions**: Do not start background services or long-running daemons. Avoid any operations that could stall or escape the sandbox. The environment is isolated; stick to file I/O, database access, and computations relevant to the repository.
* **Browser Usage**: If end-to-end tests or automation require a browser (e.g. via Playwright), use **Chromium only** (Chromium is pre-installed; other browsers like Firefox/WebKit are unavailable).
* **Primary Instructions**: This `AGENTS.md` remains the main reference for agent behavior, but supplemental modules are available. See `.github/instructions/*.instructions.md` for topic-specific guidance. Refer to those files along with this document and the user's prompt.
* **Stay On Task**: Follow the given prompt and these guidelines exactly. Do not make unrelated changes. Every command and edit should be purposeful and within scope. Avoid any explorations or modifications not relevant to the task at hand.
* **Shell Output Limits (1600-Byte Rule)**: The Codex terminal has a hard limit of \~1600 bytes per line of output. If any command outputs a line longer than this, the session **will crash and reset**. To prevent this, you **must proactively manage command output**:

  * For any command likely to produce large or continuous output (e.g. `cat` on a big file, recursive `find` or `ls -R`, using `jq` to dump a large JSON, etc.), **do not print the full output to console** outright. Instead, use safe output strategies:

    * **Strategy 2 – Log and Chunk**: Redirect the command’s output to a file (e.g. `>` to write to a log file). Then read that file in manageable chunks using tools like `head`, `tail`, or small `sed` slices. This way you can inspect contents piecewise without ever flooding the console.
    * **Strategy 3 – Use the Line Wrapper (`clw`)**: The environment includes a custom utility called **`clw`** (installed at `/usr/local/bin/clw`) specifically to mitigate long-line outputs. Pipe any potentially large output through `clw`. For example: `find / -type f | clw` or `cat largefile.txt | clw`. The `clw` tool will pass through lines under \~1550 bytes unchanged, but will **hard-wrap longer lines** at a safe length (inserting a visible “⏎” line-break marker). This ensures no single line exceeds the limit, preventing crashes.
    * **Always Pipe Large Output**: When unsure, default to piping through `clw` (`grep -R PATTERN | clw`) to avoid session resets.
    * The wrap threshold can be changed by setting the `CLW_MAX_LINE_LENGTH` environment variable (default 1550 bytes).
    * Inspect the source of `/usr/local/bin/clw` and use it exactly as documented. If `clw` is missing, recreate it using the script provided in the repository instructions and mark it executable. Pipe all commands that potentially have long output—or everything that doesn’t need a TTY—through `clw` to stay on the safe side.
    * **Example Usage:** `cat largefile.txt | clw` wraps long lines automatically. For logs, prefer `your_command > output.log` and review the log with `clw` to prevent terminal overflow.
  * These output management strategies are **mandatory** for high-risk commands. Always anticipate if a command could produce very long lines or a flood of data. When in doubt, err on the side of caution and apply one of the above methods (or use filtering commands like `grep`, `cut`, or `awk` to reduce output size). **Never** allow an unbounded output stream to print directly to the terminal.
  * **Self-Healing Recovery**: If the terminal shows `Error: Output for session 'shell' contained a line exceeding the max of 1600 bytes`, immediately start a new session, run the standard setup steps again (reactivate the virtual environment and ensure `/usr/local/bin/clw` exists), then repeat the previous command with a safe output method such as piping through `clw` or logging and chunking.
* **Anti-Recursion & Backups**: Never write backup files or any output to the repository workspace itself. All backup or log files (if any) should go to the designated external backup directory (see **GH\_COPILOT\_BACKUP\_ROOT** above). The agent should validate paths (using any provided `validate_enterprise_operation()` or similar, if available) before performing file writes, to ensure compliance with anti-recursion rules.
* **Dual Execution Pattern**: When appropriate, follow the “Dual Copilot” approach – i.e., for critical operations, simulate having a primary action followed by a validation step. (For example, after generating a script, perform a dry-run or static analysis to verify it before finalizing.)
* **Adhere to Protocol**: Always incorporate required safety checks (e.g., zero-byte file checks, recursion detection, etc.) as described in project protocols. Before concluding any major operation, ensure you run any integrity validations mandated by the project’s standards.

## Commit and PR Guidelines

To ensure your contributions can be easily reviewed and integrated, follow these conventions for commits and pull requests:

* **Conventional Commits**: Use Conventional Commits style for your commit and PR titles. For example:

  * `feat: add user login audit logging` for a new feature.
  * `fix: resolve crash on empty input in parser` for a bug fix.
  * Use a concise prefix (`feat:`, `fix:`, `docs:`, `chore:`, etc.) and a brief description of the change.
* **Pull Request Description**: Begin the PR description with a reference to the original user prompt or issue being addressed (for context). Provide a summary of what was changed and why. If the change is part of a series or has caveats, note them (e.g. mention if a new dependency is needed but wasn’t installed due to the rules).
* **Focused Scope**: Keep each PR focused on a single issue or feature. Do not lump unrelated changes together. If a task involves multiple steps or components, they can be in one PR if they are part of the same overall goal, but avoid mixing in changes that are not relevant to the main task.
* **Complete Solutions**: Only mark the task complete when the changes fully address the prompt. Partial solutions are not acceptable. Ensure that after your changes, the problem is resolved and all acceptance criteria are met.
* **Include Documentation**: If your change affects user-facing behavior or requires knowledge to use, update relevant documentation or comments. For example, if you add a new command or script, update the README or usage docs accordingly. However, avoid gratuitous edits—only change documentation as needed for your update.
* **No Extraneous Changes**: Do not perform drive-by refactoring or formatting changes that are not asked for. Every change in the diff should be attributable to solving the task at hand. Unrelated changes make review harder and may be rejected.

## Code Style and Linting

Maintain code quality and consistency with the project’s established style:

* **Follow Existing Style**: Adhere to PEP 8 for Python and the project’s conventions. Match the coding style of the surrounding code (naming, structure, patterns). If the project uses specific idioms or design patterns, try to follow those.
* **Automated Linting**: Use `ruff` for linting and formatting (as this project does). Before committing, run `ruff check .` and address any warnings or errors. Then run `ruff format .` (or ensure your changes are formatted) so that the code meets the style guidelines. The code must pass lint checks with **no** warnings.
* **Type Checking**: Run `pyright` (or `mypy` if specified) to perform static type checking. The project should remain type-clean. If your changes introduce type errors, fix them or adjust type annotations as needed. Do not ignore type checker output.
* **Clean and Commented Code**: Remove any debugging prints or leftover test code before committing. Comments and docstrings should be added for complex logic or important sections, following the project’s commenting style. Keep comments clear and helpful, but avoid redundant comments for self-explanatory code.

## Testing and Validation

Before submitting, ensure that all tests pass and that you have added new tests if you introduced new functionality:

* **Run All Tests**: Use `pytest` (or the project’s test runner) to run the test suite. For example:

  * Run specific test modules if you know what area is affected (e.g. `pytest tests/test_server.py` for server-side changes, or `pytest tests/test_web.py` for front-end/UI changes).
  * If unsure, run `pytest` without arguments to run all tests.
* **Passing Tests Required**: All tests **must pass** before completion. If tests are failing, investigate and fix the issues. Do not assume failing tests are “not relevant” – if a test is failing, either your change broke something or the test needs updating due to intentional changes in behavior.
* **Add Tests for New Code**: When you implement new features or fix bugs, add corresponding tests:

  * If you fix a bug, add a test that would have caught that bug to prevent regressions.
  * If you add a new feature, write tests for its expected behavior (including edge cases).
  * Place new tests in the appropriate file under `tests/` (matching the structure, e.g., server-related tests in `test_server.py`, UI tests in `test_web.py`, etc.).
* **Iterate as Needed**: If your new tests reveal issues or if you discover new failing cases, fix the code and re-run tests until everything passes.
* **Automated Checks**: In addition to tests, ensure linting and type checks are green (as noted in the Code Style section). The CI or maintainers will run these, so you should too, to catch issues early.

## Project Structure and Conventions

Understand the repository structure and place your changes appropriately:

* **Match the Structure**: Add new files or modules only if necessary, and put them in the correct location. For example, backend logic should reside in the backend-related directory or module, frontend code in the frontend directory, etc., following how the project is organized. Do not create new top-level directories. Instead, integrate with the existing structure.
* **Key Directories**: Be aware of important directories:

  * `tests/` – contains test cases (unit tests, integration tests). Update or add here for any code changes.
  * `scripts/`, `server/`, `client/` (or similar) – the exact structure depends on the project, but follow the established pattern. For instance, if there’s a `database/` or `utils/` directory, put new database-related or utility scripts there rather than at root.
  * `config/` – contains configuration files (like `enterprise.json` or others). If you need to change defaults or add config, ensure it goes through these files.
* **Consistency**: Follow naming conventions already in use. E.g., if existing classes use CamelCase, do the same; if functions\_are\_snake\_case, stick to that. Consistent naming and organization make the codebase maintainable.
* **Avoid Duplicates**: Do not duplicate existing functionality. Before writing new code, check if similar functionality exists that you can extend or reuse. Only create a new file or function if you’re sure the logic isn’t already present. Redundant code will be rejected.
* **Documentation Updates**: If your change alters how the system works (for example, changes a command-line interface, adds an environment variable, affects deployment, etc.), update relevant documentation in `README.md` or the `docs/` folder. Make sure instructions remain accurate. Also update in-line docstrings or comments if behavior changes.

## Agent Roles

In the **gh\_COPILOT** toolkit, multiple conceptual “agent” components work together. The AI agent should be aware of these roles to understand the context of the system (note: some are aspirational or in development):

| Agent System                            | Core Function                                                                                                                |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **DualCopilotOrchestrator**             | Primary executor with a secondary validator (dual-agent pattern for critical tasks).                                         |
| **UnifiedMonitoringOptimizationSystem** | Continuous health monitoring of the system (ensures uptime, performance metrics).                                            |
| **QuantumOptimizationEngine**           | *Aspirational:* placeholder for quantum optimization features (not fully implemented, do not rely on actual quantum output). |
| **UnifiedScriptGenerationSystem**       | Generates scripts based on patterns from `production.db` (automating common tasks using database-driven templates).          |
| **UnifiedSessionManagementSystem**      | Manages session integrity (zero-byte file checks, anti-recursion enforcement, ensures each session starts/ends cleanly).     |
| **UnifiedDisasterRecoverySystem**       | Handles backup and restore processes (enterprise backup compliance and recovery protocols).                                  |
| **LegacyCleanupSystem**                 | Performs cleanup of legacy files and workspace tidying (archiving old data, removing deprecated files).                      |
| **WebGUIIntegrationSystem**             | Integrates with the Web Dashboard UI (exposes endpoints, updates dashboard with status logs and metrics).                    |
| **EnterpriseComplianceValidator**       | Runs security and compliance audits (ensures changes meet enterprise rules and regulations).                                 |
| **CompleteConsolidationOrchestrator**   | Orchestrates database consolidation (merging or optimizing `production.db` and other databases).                             |

*Be mindful of these roles when writing code or documentation. For example, if you write a backup script, ensure it aligns with **UnifiedDisasterRecoverySystem** protocols, or if outputting logs or metrics, consider the **WebGUIIntegrationSystem** expectations.* Many of these systems implement the dual-copilot validation and other enterprise patterns.

## Core Protocols

The gh\_COPILOT project adheres to several core protocols and standards that the agent must follow in its solutions:

1. **Database-First Operations** – Always query or utilize `production.db` (and related databases) as the primary source of truth before making filesystem changes. Database files must remain under **99.9 MB** each (monitor sizes if your task involves DB migrations or insertions).
2. **Dual Copilot Pattern** – Implement a dual-phase approach for critical workflows: a primary action followed by a validation or review step by a secondary process. This ensures every major operation is verified by an independent check within the automation.
3. **Visual Processing Indicators** – Any long-running script should include user-friendly indicators (progress bars, timestamps for start/end, ETA calculations, and real-time status updates). This aligns with enterprise UI/UX standards for long processes.
4. **Anti-Recursion & Backup Rules** – Absolutely no recursive copying of the workspace. Backups must be stored in the external backup directory (never inside the workspace). Always validate paths and use provided safety checks (e.g., `validate_enterprise_operation()` if available) before file operations to enforce this.
5. **Session Integrity & Continuous Operation** – Each session or run should begin and end with integrity checks (e.g., ensure no zero-byte files introduced, all expected processes completed). The system is expected to run continuously 24/7, so any automation should be robust to long uptimes and not degrade over time.
6. **Response Chunking** – (For AI responses in multi-turn scenarios) Keep responses under \~2000 tokens (aim for 1500–1800 for readability). Break down large outputs into logically separate chunks or phases. Each chunk of output or code should end with a clear validation or summary, and possibly a hand-off to the next chunk. This ensures manageability and clarity in review.
7. **Quantum & AI Protocols** – Quantum computing features and certain advanced AI functions are currently **aspirational**. They should be treated as placeholders or experimental. Do not rely on them for critical logic. If you integrate with these parts, clearly mark outputs as simulated or placeholder. Ensure that the presence of these features doesn’t break core functionality if they are inactive.

By adhering strictly to the above guidelines and protocols, the AI agent will produce contributions that are consistent with the project’s standards and less likely to be rejected. **Always double-check your work against these rules before considering the task complete.**

---

*Following these instructions is mandatory for all AI-driven contributions to **gh\_COPILOT**. Deviation from these guidelines may result in the pull request being declined or the agent’s changes being reverted. Stay within the bounds of the guide, and focus on delivering value aligned with the project’s goals and constraints.*

---

**Sources and References:** Best practices distilled from the gh\_COPILOT documentation and environment, including environment config examples and the Codex known limitations. Adherence to these guidelines ensures smooth operation within the ChatGPT–Codex environment and compliance with enterprise requirements.

- Inspect the source of /usr/local/bin/clw and use it as indicated.
- Pipe all commands that potentially might have a long output, or pipe everything that does not need a tty to stay on the safe side.
