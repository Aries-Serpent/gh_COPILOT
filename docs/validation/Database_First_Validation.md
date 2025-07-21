# Database-First Validation Guide

This document describes how to verify that automation follows the database-first workflow.

## Checklist

1. **Environment Setup** – Ensure `GH_COPILOT_WORKSPACE` and `GH_COPILOT_BACKUP_ROOT` are set.
2. **Initial Query** – Confirm each script queries `production.db` before creating files.
3. **Record Keeping** – Validation results should be stored in `validation_logs.db`.
4. **Dual Copilot Review** – After primary execution, run the secondary validator to cross-check results.

Use these steps whenever new modules or templates are introduced.
