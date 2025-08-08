# Codex Logging

This document describes how Codex sessions are recorded in the
`databases/codex_log.db` SQLite database and how to commit updates
responsibly.

## Database Schema

The database contains two tables:

| Table | Purpose | Columns |
|-------|---------|---------|
| `codex_actions` | Records individual actions taken during a session. | `id INTEGER PRIMARY KEY`, `session_id TEXT`, `ts TEXT`, `action TEXT`, `statement TEXT`, `metadata TEXT` |
| `codex_log` | Tracks session start and end events. | `session_id TEXT`, `event TEXT`, `summary TEXT`, `ts TEXT` |

## Usage

Utilities in `utils/codex_log_db.py` manage the database:

```python
from utils import codex_log_db

codex_log_db.log_codex_start(session_id)
codex_log_db.log_codex_action(session_id, "action", "statement", "meta")
codex_log_db.log_codex_end(session_id, "summary")
```

Use `codex_log_cursor()` for batch inserts and `init_db()` to create the
tables if they do not exist.

## Required Environment Variables

Before logging, set:

- `GH_COPILOT_WORKSPACE` – absolute path to the repository root.
- `GH_COPILOT_BACKUP_ROOT` – external directory for backups.
- `ALLOW_AUTOLFS` – set to `1` to allow automatic Git LFS tracking.

## Commit Process and Git LFS

`codex_log.db` is a binary artifact stored under `databases/` and managed with
Git LFS. When committing session data:

1. Run `git lfs install` if not already configured.
2. Verify tracking with `git lfs ls-files | grep codex_log.db`.
3. Stage the database with `git add databases/codex_log.db`.
4. Commit alongside related code or documentation changes.

Git LFS ensures the repository remains lightweight and avoids corruption of
the database file. Refer to `docs/git_lfs_recovery.md` for recovery procedures
if LFS data becomes inconsistent.

