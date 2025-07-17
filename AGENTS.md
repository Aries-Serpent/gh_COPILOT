# AGENTS.md – gh_COPILOT Toolkit

## Overview

This document defines all agent roles—**human and automated**—in the gh_COPILOT Toolkit (v4.0).  
All agents are responsible for strict adherence to enterprise protocols:  
- **Database-First Operations**
- **Dual Copilot Validation**
- **Anti-Recursion & Backup Rules**
- **Mandatory Visual Progress Indicators**
- **Session Integrity & Continuous Operation**
- **Chunked Responses**

**Quantum features** remain aspirational until backed by functional, validated code. No placeholder logic is permitted in production.  
_This guide is optimized for use by ChatGPT-CODEX and similar agents._

---

## Human Agent Roles

| Role                    | Description                                                                                       |
|-------------------------|---------------------------------------------------------------------------------------------------|
| **Lead System Architect**    | Approves all architecture, system design, and compliance.                                         |
| **DevOps Engineer**          | Manages CI/CD, infrastructure, Docker, and deployment.                                            |
| **AI/ML Specialist**         | Implements, validates, and documents all AI and quantum features.                                 |
| **Full-Stack Developer**     | Extends unified systems, APIs, and web GUIs.                                                     |
| **Compliance Officer**       | Validates anti-recursion, backup policies, and session integrity.                                 |
| **Database Engineer**        | Maintains, optimizes, and enforces schema/database-first protocols.                               |

---

## Automated Agent Roles

| Agent Name                       | Responsibility & Scope                                                                                       |
|----------------------------------|-------------------------------------------------------------------------------------------------------------|
| **DualCopilotOrchestrator**      | Executes critical flows and validates all outputs (primary+secondary).                                       |
| **UnifiedMonitoringOptimizationSystem** | Provides continuous system health monitoring, analytics, and optimization.                          |
| **QuantumOptimizationEngine**    | (Planned) Implements real quantum optimizations—**no stubs allowed in production**.                         |
| **UnifiedScriptGenerationSystem**| Generates scripts and code strictly from `production.db` templates/patterns.                                 |
| **UnifiedSessionManagementSystem**| Enforces zero-byte file checks, anti-recursion, and session logging at boundaries.                        |
| **UnifiedDisasterRecoverySystem**| Handles backup/restore events, disaster recovery workflows.                                                  |
| **LegacyCleanupSystem**          | Cleans up workspace, archives legacy assets, prevents workspace bloat.                                       |
| **WebGUIIntegrationSystem**      | Provides web dashboard endpoints, integrates UI monitoring and reporting.                                    |
| **CI/CD Workflows**              | Automates lint, test, build, and deployment processes.                                                       |
| **EnterpriseComplianceValidator**| Audits all security and protocol compliance; logs all critical actions.                                      |

> **Agent Lifecycle:** Register new agents here; deprecate legacy roles in this file.  
> **Audit Logging:** All agent actions must be logged to the audit database for traceability.

---

## Core Agent Protocols

### 1. Database-First Operations
> All file, code, and cognitive tasks must **first query `production.db`** (and any related schemas) for templates/patterns prior to performing any filesystem operations.

### 2. Dual Copilot Pattern
- Every critical workflow must utilize:
  - **Primary Executor**: Executes action, logs outputs, visual progress.
  - **Secondary Validator**: Validates output, context, and conformance to all standards.

### 3. Visual Processing Compliance
- Every Copilot/agent action must provide visual, **plain-text progress indicators** (e.g., progress bars/logs).
- No emojis—cross-platform, text-based only.
- See `final_enterprise_orchestrator.py` for reference.

### 4. Anti-Recursion & Backup Rules
- Never create backup folders inside the workspace.
- All backups must reside in `E:/temp/gh_COPILOT_Backups`.
- Validate backup paths with `validate_enterprise_operation()`.
- Scan for zero-byte files at **session start and end**.

### 5. Session Integrity & Continuous Operation
- Integrity checks and session logs are required at every session boundary.
- Monitoring and optimization systems must run in **continuous operation** (Phase 4+).

### 6. Chunked Responses
- All agent responses must be chunked under **2,000 tokens** (preferably 1,500–1,800).
- Each chunk: starts with anti-recursion validation, provides context, details, next-step transition.

### 7. Quantum & AI Protocols
- **No quantum/AI features are considered implemented unless**:  
  - Fully functional code exists in the repo.
  - Accompanied by passing tests and updated documentation.
- No references to incomplete/placeholder quantum features are permitted in production.

---

## Coding, Contribution & Audit Standards

- **Type hints and docstrings required** for all agent scripts.
- Follow **PEP 8** and **flake8**.
- Use `autopep8` and `isort` for formatting; lint with `flake8`.
- Never modify bundled or version-controlled SQLite databases.
- Always update/create tests when code changes; run `make test`.
- **Short, imperative commit messages only.**
- Store and validate documentation metrics using:
  - `scripts/generate_docs_metrics.py`
  - `scripts/validate_docs_metrics.py`

---

## Agent Registration & Deprecation

- All new agents must be registered in this file with a clear role and responsibility.
- Deprecate or update obsolete agent roles as the platform evolves.
- All agents log critical actions to the audit database for compliance and traceability.

---

## Summary

Every agent—human or automated—must internalize and adhere to the protocols above.  
**No agent is permitted to bypass database-first logic, anti-recursion protocols, or visual compliance.**  
Quantum features remain aspirational until actual code, tests, and documentation exist.

*This AGENTS.md is designed for direct use by ChatGPT-CODEX and automated workflows.*

---
