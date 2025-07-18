# AGENTS Guide for ChatGPT Codex

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
