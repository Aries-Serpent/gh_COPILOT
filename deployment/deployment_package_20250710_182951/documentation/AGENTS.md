# AGENTS Guide

## Repository & Environment Overview

The **gh\_COPILOT Toolkit v4.0** repository supports enterprise deployment, monitoring, and automation, featuring modular unified systems, AI/quantum integration, and compliance-driven architecture.
**Note:** All references to "quantum optimization" or quantum algorithms are in draft form and must be fully implemented, researched, and validated by ChatGPT Codex—**no placeholder or speculative logic should remain** in production code.

### Environment Setup

* **Python 3.8+** is required (see `pyproject.toml` for the precise version).
* Install core dependencies:

  * `pip install -r requirements.txt`
  * Optionally:

    * `pip install -r requirements-web.txt` (for web dashboard)
    * `pip install -r requirements-ml.txt` (for machine learning/AI features)
* Tests: `make test` (installs `requirements-test.txt` and runs `pytest`)
* Set workspace root via `GH_COPILOT_WORKSPACE` (default `/path/to/workspace`).

---

## Agent Roles & Responsibilities

### 1. **Human Agents**

| Role                      | Scope                                          | Permissions     | Key Responsibilities                                  |
| ------------------------- | ---------------------------------------------- | --------------- | ----------------------------------------------------- |
| **Lead System Architect** | All systems/modules, environment, compliance   | Admin, Approver | Oversee architecture, review audits, approve changes  |
| **DevOps Engineer**       | CI/CD, infra, containerization, environment    | Admin           | Maintain deployment, Docker, CI/CD pipelines          |
| **AI/ML Specialist**      | AI, ML, quantum placeholder logic              | Write, Review   | Implement/validate AI features, quantum integration   |
| **Full-stack Developer**  | Unified systems, Web-GUI, database integration | Write, Review   | Code, extend, and maintain unified system modules     |
| **Compliance Officer**    | Security, compliance, audit                    | Read, Approve   | Validate anti-recursion, zero-byte, session integrity |
| **Database Engineer**     | Database schema, migration, integration        | Write, Review   | Maintain and optimize all database schemas and sync   |

### 2. **Automated/AI Agents**

| Agent Name                      | Class / Script                        | Core Function                                    | Triggers/Scope                      | Authority                 |
| ------------------------------- | ------------------------------------- | ------------------------------------------------ | ----------------------------------- | ------------------------- |
| **Dual Copilot Executor**       | `DualCopilotOrchestrator`             | Primary AI execution + secondary validation      | All system-critical workflows       | Gatekeeper, Validator     |
| **Unified Monitoring Agent**    | `UnifiedMonitoringOptimizationSystem` | 24/7 system health, optimization, analytics      | Continuous operation, triggers      | Read/Alert/Optimize       |
| **Quantum Placeholder Agent**   | `QuantumOptimizationEngine`           | Quantum-inspired/classical fallback optimization | Advanced optimization phases        | Aspirational/Experimental |
| **Script Generation Agent**     | `UnifiedScriptGenerationSystem`       | DB-driven script generation (16,500+ patterns)   | Script requests, template changes   | Write/Generate/Validate   |
| **Session Integrity Agent**     | `UnifiedSessionManagementSystem`      | Zero-byte, anti-recursion, session integrity     | Session lifecycle                   | Gatekeeper/Enforcer       |
| **Disaster Recovery Agent**     | `UnifiedDisasterRecoverySystem`       | Backup, restore, DR compliance                   | Scheduled/triggered ops             | Critical, Emergency       |
| **Legacy Cleanup Agent**        | `UnifiedLegacyCleanupSystem`          | Archival, workspace cleanup, file classification | Cleanup cycles, compliance triggers | Write/Archive             |
| **Web-GUI Interface Agent**     | `WebGUIIntegrationSystem`             | Dashboard endpoint orchestration & real-time UI  | Web/API requests                    | User/Interface Layer      |
| **CI/CD Pipeline Agent**        | `.github/workflows/*`, `ci_cd.yml`    | Lint, test, build, and auto-deploy on commit     | Code push/PR                        | Enforcer/Blocker          |
| **Compliance Validation Agent** | `EnterpriseComplianceValidator`       | Enterprise compliance & security policy checks   | Pre-merge, scheduled, on-demand     | Audit/Report/Block        |

---

## Agent Interfaces, Protocols & Compliance

* **API/Method Interfaces:**
  Agents expose documented public methods (see system docstrings and interface docs).
* **Triggering Events:**

  * On commit, push, PR: CI/CD Agent
  * On session start/end: Session Integrity Agent, Monitoring Agent
  * On dashboard/API call: Web-GUI Agent
  * On scheduled DR/compliance event: Disaster Recovery Agent, Compliance Validator
* **Validation Flows:**

  * Dual Copilot Executor *must* validate high-impact/production actions.
  * All agents log critical actions to operations/audit databases.
* **Session Protocols:**

  * Start session: `COMPREHENSIVE_WORKSPACE_MANAGER.ps1 -SessionStart`, then run validation and emergency cleanup scripts.
  * End session: `COMPREHENSIVE_WORKSPACE_MANAGER.ps1 -SessionEnd`, final anti-recursion/zero-byte check.
  * All file operations validated by `validate_enterprise_operation()` to enforce workspace root, ban recursion, and validate backup paths.

---

## Autonomous File & Workspace Management

* Scripts and agents **must query `production.db`** for organization/classification patterns.
* The **Primary Executor/Secondary Validator** model enforces separation of duties and cross-validation.
* Anti-recursion compliance is enforced on all file operations, both by human and AI agents.

---

## Quantum & AI Protocols

* All quantum optimization and/or quantum algorithm capabilities are **in draft** and must be **explicitly, fully implemented** and validated by ChatGPT Codex before claiming production status.
* Placeholders are **not permitted** in production code—replace with functional, tested algorithms and supporting documentation.
* Keep documentation synchronized with code; treat quantum/AI section changes as high priority for review.

---

## Coding, Testing, and Review Conventions

* Follow **PEP 8/flake8** style, type hints, and docstrings.
* Use `autopep8` and `isort` for formatting; `flake8` for linting.
* Do **not** modify bundled SQLite files under version control.
* Always create/update tests when changing scripts, run `make test`, and maintain `GH_COPILOT_WORKSPACE` env var.
* Commit messages should be short, imperative, and clear.

---

## Response Chunking & Copilot Interactions

* When interacting with Copilot, **responses must be chunked** <2,000 tokens (preferably 1,500–1,800).
* Chunks should begin with anti‑recursion validation and, if relevant, workspace compliance checks.

---

## Agent Lifecycle Management

* **Register new agents/scripts** in this file and document in code.
* Deprecate/retire legacy agents per cleanup protocols; flag in code and in this document.
* All agents require automated/manual testing before production use.
* Agents must support the advancement audit, gap analysis, and compliance review process.

---

## Roadmap for Agent Evolution

* **Phase 6+**: Prepare for quantum circuit agent integration (API stubs, compliance for quantum/cloud execution).
* **Continuous Improvement**: All agents must adapt to new compliance/security mandates and evolving enterprise standards.

---

## Revision Log

| Date       | Editor      | Change Summary                                                                                                                                           |
| ---------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2025-07-08 | Marc J/Chat | Unified and enhanced agent guide for v4.0, merged AI, human, and automation protocols, clarified quantum/AI status, and updated compliance requirements. |

---

*See technical whitepaper and module docstrings for further agent implementation and interface details.*